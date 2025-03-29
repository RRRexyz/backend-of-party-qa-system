import getpass, httpx, xml.dom.minidom


def authenticate(sduid: str, password: str):
    baseURL = "https://pass.sdu.edu.cn/"
    ticket = httpx.post(
        "https://pass.sdu.edu.cn/cas/restlet/tickets",
        content=f"sduid={sduid}&password={password}",
    ).text
    if not ticket.startswith("TGT"):
        raise Exception("ticket should start with TGT. Check your sduid and password.")
    sTicket = httpx.post(
        "https://pass.sdu.edu.cn/cas/restlet/tickets/" + ticket,
        content="service=https://service.sdu.edu.cn/tp_up/view?m=up",
        headers={"Content-Type": "text/plain"},
    ).text
    if not sTicket.startswith("ST"):
        raise Exception("sTicket should start with ST")
    user_data = xml.dom.minidom.parseString(
        httpx.get(
            "https://pass.sdu.edu.cn/cas/serviceValidate",
            params={
                "ticket": sTicket,
                "service": "https://service.sdu.edu.cn/tp_up/view?m=up",
            },
        ).text
    )
    name = user_data.getElementsByTagName("cas:USER_NAME")[0].childNodes[0].data
    student_id = user_data.getElementsByTagName("sso:user")[0].childNodes[0].data
    return name, student_id


sduid = input("Please input your sduid: ")
password = getpass.getpass("Please input your password: ")
print(authenticate(sduid, password))
