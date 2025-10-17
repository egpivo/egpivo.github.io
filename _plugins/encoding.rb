# Ensure Ruby treats file paths and IO as UTF-8 so Jekyll can process
# posts with multibyte characters (e.g., Chinese titles) without errors.
Encoding.default_external = Encoding::UTF_8
Encoding.default_internal = Encoding::UTF_8
