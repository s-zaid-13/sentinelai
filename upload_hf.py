from huggingface_hub import HfApi

api = HfApi()

# Apna Hugging Face username daalo yahan
api.create_repo(
    repo_id="samamazaid/sentinelai-distilbert", repo_type="model", private=False
)

api.upload_folder(
    folder_path="models/saved_model",
    repo_id="samamazaid/sentinelai-distilbert",
    path_in_repo="saved_model",
)

api.upload_file(
    path_or_fileobj="models/thresholds.json",
    path_in_repo="thresholds.json",
    repo_id="samamazaid/sentinelai-distilbert",
)
