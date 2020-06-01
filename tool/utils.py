from google.cloud import automl_v1beta1 as automl

from toolssite.settings import get_env_var


def check_news(title: str, text: str):
    project_id = get_env_var('PROJECT_ID', '', '')
    compute_region = get_env_var('COMPUTE_REGION', '', '')
    model_display_name = get_env_var('MODEL_DISPLAY_NAME')

    client = automl.TablesClient(
        project=project_id,
        region=compute_region,
    )

    response = client.predict(
        model_display_name=model_display_name,
        inputs={
            "title": title,
            "text": text,
        },
    )

    for result in response.payload:
        if result.tables.value.string_value == 'true':
            return result.tables.score

    return None
