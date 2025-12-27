def success(data=None, meta=None):
    return {
        "status": "success",
        "data": data,
        "meta": meta
    }

def error(message, code):
    return {
        "status": "error",
        "message": message,
        "code": code
    }