cd deployment_templates
cd .. && make clean-uat create-uat && cd deployment.uat && make down && make build-up

python ttk_plugin/src/lyik/ttk/models/forms/PDFWriter8.py
Filling Switzerland6 PDF form with sample data... passport_details.gender.value M 
Sample data for Switzerland6: passport_details.gender.value == GENDER.M False  passport_details.gender.value M
/Users/dineshpratapsingh/lyik/lyik_ttk/ttk_plugin/src/lyik/ttk/models/forms/PDFWriter2.py:39: PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
  data_dict = model_data.dict()
✅ Filled PDF saved as: Switzerland6_original.pdf_filled.pdf

python ttk_plugin/src/lyik/ttk/models/forms/model_generator1.py
