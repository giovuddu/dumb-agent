import os
from config import SYSTEM_PROMPT
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_files_content, get_file_content
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

from arg_parser import parse_args

load_dotenv()

MODEL = "gemini-2.0-flash-001"

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_files_content,
        schema_run_python_file,
        schema_write_file,
    ]
)


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    if function_call_part.name == "get_files_info":
        res = get_files_info(
            working_directory="./calculator", **function_call_part.args
        )
    elif function_call_part.name == "get_file_content":
        res = get_file_content(
            working_directory="./calculator", **function_call_part.args
        )
    elif function_call_part.name == "run_python_file":
        res = run_python_file(
            working_directory="./calculator", **function_call_part.args
        )
    elif function_call_part.name == "write_file":
        res = write_file(working_directory="./calculator", **function_call_part.args)
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": res},
            )
        ],
    )


def main(user_prompt, verbose=False):
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    api_key = os.environ.get("GEMINI_API_KEY", None)
    client = genai.Client(api_key=api_key)

    loops = 0
    while loops < 20:
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=SYSTEM_PROMPT
                ),
            )

            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content is not None:
                        messages.append(candidate.content)

            if response.usage_metadata is None:
                raise Exception("Gemini has gone away...")
            else:
                if verbose:
                    print(f"User prompt: {user_prompt}")
                    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
                    print(
                        "Response tokens:",
                        response.usage_metadata.candidates_token_count,
                    )

                print(response.text)
                if response.function_calls:
                    results = []
                    for function_call in response.function_calls:
                        print(
                            f"Calling function: {function_call.name}({function_call.args})"
                        )
                        res = call_function(function_call)
                        if (
                            res.parts is None
                            or res.parts[0].function_response is None
                            or res.parts[0].function_response.response is None
                        ):
                            raise Exception
                        else:
                            results.append(res.parts[0].function_response.response)
                            if verbose:
                                print(f"-> {res.parts[0].function_response.response}")
                    print(results)
                    messages.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(text=result["result"]) for result in results
                            ],
                        )
                    )
            if response.text is not None and response.function_calls is None:
                break
        except Exception as exc:
            messages.append(
                types.Content(role="user", parts=[types.Part(text=exc.__str__())])
            )

    loops += 1


if __name__ == "__main__":
    args = parse_args()
    main(args.prompt, args.verbose)
