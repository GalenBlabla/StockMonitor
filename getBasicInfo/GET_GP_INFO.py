import requests as res


def get_info(word):
    MY_URL = 'http://ai.10jqka.com.cn/java-extended-api/highlight/tag/get?code='+word
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "Cookie": "@#!userid!#@=574831162; v=AxsM2oe0_ICfbAB0dXFMj8OdrHWE8C_yKQTzpg1Y95ox7DVqlcC_QjnUg-Ae; escapename=mx_574831162; ticket=ccd754e8a94a0acc466235a82e8c18e2; u_name=mx_574831162; user=MDpteF81NzQ4MzExNjI6Ok5vbmU6NTAwOjU4NDgzMTE2Mjo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoxNjo6OjU3NDgzMTE2MjoxNjYzMjA1NTAyOjo6MTYxNzE2NTQ4MDo2MDQ4MDA6MDoxNmIwZTY2NmQ1YzViNzcxNWFiZTg5YjQ2ZTJkYjc2Zjk6OjA%3D; user_status=0; userid=574831162; searchGuide=sg"
    }

    rep = res.get(MY_URL,headers=headers).json()
    # print(rep)
    rep2 = rep['data']
    msg_list=[]
    if(rep2 != None):
        for i in rep2:
            # print(i)
            # print(i["tagName"])
            # print(i["isBull"])
            # print(i["query"])
            # print(i["type"])
            # print(i["abstractText"])
            # print(i["frequency"])
            msg = "标签名：\t"+str(i["tagName"])+"\n号码："+str(i["query"])+"\n类型： "+str(i["type"])+"\n简介："+str(i["abstractText"])+"\n \n"
            # print(msg)
            msg_list.append(msg)
        # print(msg_list)
        return msg_list

# print(get_info("002439"))

