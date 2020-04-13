import json
import sys
import os
import argparse
from cp_common_functions import *

MODULE_NAME = "ImageMath"
OUTPUT_FILENAME = "output.cppipe"

operator_map = {
    "add": "Add",
    "subtract": "Subtract",
    "multiply": "Multiply",
    "divide": "Divide",
    "average": "Average",
    "minimum": "Minimum",
    "maximum": "Maximum",
    "invert": "Invert",
    "log_2": "Log transform (base 2)",
    "log_legacy": "Log transform (legacy)",
    "and": "And",
    "or": "Or",
    "not": "Not",
    "equals": "Equals"
}


def build_main_block(input_params):
    """Creates the main block of the CP pipeline with the parameters that don't depend on conditional choices"""
    operation = operator_map[input_params['operation']['operation']]
    result = INDENTATION.join(
        [f"{INDENTATION}Operation:{operation.encode('utf-16')}\n",
         f"Raise the power of the result by:{input_params['operation']['op_results']['raise_the_power_of_the_result_by']}\n",
         f"Multiply the result by:{input_params['operation']['op_results']['multiply_the_result_by']}\n",
         f"Add to result:{input_params['operation']['op_results']['add_to_result']}\n",
         f"Set values less than 0 equal to 0?:{input_params['operation']['op_results']['set_values_less_than_0_equal_to_0']}\n",
         f"Set values greater than 1 equal to 1?:{input_params['operation']['op_results']['set_values_greater_than_1_equal_to_1']}\n",
         f"Ignore the image masks?:{input_params['ignore_the_image_masks']}\n",
         f"Name the output image:{input_params['name_output_image']}"
         ])
    return(result)

def build_variable_block(inputs_galaxy):
    result=""
    if "first_image" in inputs_galaxy['operation']:
        first_image_block = build_first_image_block(inputs_galaxy['operation']['first_image'])
        result = "\n".join([result, first_image_block])
    if "second_image" in inputs_galaxy['operation']:
        second_image_block = build_second_image_block(inputs_galaxy['operation']['second_image'])
        result = "\n".join([result, second_image_block])
    return (result)


def build_first_image_block(input_params):
    """Creates the block of parameters for the first operator in operations"""
    result = INDENTATION.join(
        [f"{INDENTATION}Image or measurement?:{input_params['image_or_measurement']['image_or_measurement']}\n",
         f"Select the first image:{input_params['image_or_measurement']['select_the_first_image']}\n",
         f"Multiply the first image by:{input_params['multiply_the_first_image_by']}\n",
         f"Measurement:{get_json_value_from_path(input_params,'image_or_measurement/measurement')}"
         ])
    return(result)


def build_second_image_block(input_params):
    """Creates the block of parameters for the second operator in binary operations"""
    result = INDENTATION.join(
        [f"{INDENTATION}Image or measurement?:{input_params['image_or_measurement']['image_or_measurement']}\n",
         f"Select the second image:{input_params['image_or_measurement']['select_the_second_image']}\n",
         f"Multiply the second image by:{get_json_value_from_path(input_params,'multiply_the_second_image_by')}\n",
         f"Measurement:{get_json_value_from_path(input_params,'image_or_measurement/measurement')}"
         ])
    return(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--pipeline',
        help='CellProfiler pipeline'
    )
    parser.add_argument(
        '-i', '--inputs',
        help='JSON inputs from Galaxy'
    )
    args = parser.parse_args()

    pipeline_lines = get_pipeline_lines(args.pipeline)
    inputs_galaxy = json.load(open(args.inputs, "r")) 

    current_module_num = get_total_number_of_modules(pipeline_lines)
    current_module_num += 1
    pipeline_lines = update_module_count(pipeline_lines, current_module_num)

    header_block = build_header(MODULE_NAME, current_module_num)
    main_block = build_main_block(inputs_galaxy)
    variable_block = build_variable_block(inputs_galaxy)

    module_pipeline = f"\n{header_block}{main_block}{variable_block}"
    pipeline_lines.append(module_pipeline)

    write_pipeline(OUTPUT_FILENAME, pipeline_lines)
