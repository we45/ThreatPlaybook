project_response_schema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "properties": {
                "createProject": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
}