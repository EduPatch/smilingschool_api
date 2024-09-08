import login, os, ast
import runner
from runner import Method

def main():
    #imobj = login.Im(cookiefile="cookiefile" if os.path.isfile("cookiefile") else None)
    #response = imobj.post(url="https://hub.infomentor.se/NotificationApp/NotificationApp/GetNotifications", allow_redirects=False)
    #print(response.content, "\n", response.status_code, "\n", response.url)
    rundata = runner.data
    #print(rundata)
    #response = make_request(imobj, rundata["request"])
    swag = craft_swag(rundata)#, response)

def determine_data_type(data):
    data_type = ""
    data_format = None
    try:
        match data:
            case str():
                data_type = "string"
                data_format = input(f"What openapi format is this? \"{data}\"").trim().lower()
            case dict():
                data_type = "object"
            case int():
                data_type = "integer"
                data_format = input(f"What openapi format is this? \"{data}\"").trim().lower()
            case float():
                data_type = "number"
                data_format = input(f"What openapi format is this? \"{data}\"").trim().lower()
            case bool():
                data_type = "object"
            case list():
                data_type = "array"
            case _:
                raise Exception()
    except:
        data_type = input(f"Type couldn't be determined. Please input the swagger type name of this data!\n\"{data}\"\n> ").trim().lower()
        data_format = input(f"What openapi format is this? \"{data}\"").trim().lower()
    return (data_type, data_format)


def craft_swag(data):#, response):
    final_swag = {
        f"{data['path']}": {
            f"{data['request']['method'].value}": {
                "tags": data['tags']
            }
        }
    }

    if data['request']['method'] == Method.POST:
        data_type = ""
        schema_data_type = determine_data_type(data['request']['data'])
        try:
            match data['request']['data']:
                case str():
                    data_type = "text/plain; charset=utf-8"
                    #input(f"What openapi string format is this? \"{}\"")
                case dict():
                    data_type = "application/json"
                case _:
                    raise Exception()
        except:
            print("POST data type couldn't be determined")
            data_type = "text/plain; charset=utf-8"
            #input("Type couldn't be determined. Please input the swagger type name of this response!\n> ").trim().lower()
        
        request_schema = {
            "schema": {
                "type": schema_data_type[0]
            }
        }
        if schema_data_type[1] != None:
            request_schema['schema']['format'] = schema_data_type[1]

        request_body = {
            "content": {
                f"{data_type}": request_schema
            }
        }
        final_swag[data['path']][data['request']['method'].value]['requestBody'] = request_body

    print(final_swag)

def make_request(imobj, request_data):
    response = ()
    match request_data['method']:
        case Method.POST:
            response = imobj.post(url=request_data['url'], data=request_data['data'], params=request_data['params'], allow_redirects=False)
        case Method.GET:
            response = imobj.get(url=request_data['url'], params=request_data['params'], allow_redirects=False)
    try:
        return response.json()
    except:
        return response.content.decode('utf8')

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()