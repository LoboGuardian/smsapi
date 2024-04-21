import os
import typing as ty
import aiofiles
import aiohttp
import aiohttp.client
import uvicorn
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()

async def fileopen(filename: str) -> ty.List[str]:
    async with aiofiles.open(filename, 'r') as file:
        return [line.strip() for line in await file.readlines()]

async def save_failed_contacts(failed_contacts: ty.List[str]) -> None:
    if failed_contacts:
        with open('failed_contacts.txt', 'w') as file:
            file.write('\n'.join(failed_contacts))

async def send_message(session: aiohttp.client.ClientSession, contact: str, templateid: str) -> None:
    url = "https://automate.nexgplatforms.com/api/v1/wa/multi-send"
    data = {
        "serviceType": "transactional",
        "mediaTransid": "",
        "templateid": templateid,
        "fromNumber": "919711629809",
        "msgDetails": [
            {
                "messageType": "template",
                "contactnumber": contact,
                "messageid": "3fbdd0b1-030f-4359-b21c-3202f6762088",
                "dynamicUrl": "",
                "message": ""
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "Authorization": "cTlQLW44Mi05aFF1UEoxUmw3VGp5MGlxRFpqWkdXRXRTVHViUUk3d3VrSTo=",
        "content-type": "application/json"
    }

    try:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to send to contact: {contact}. Status code: {response.status}")
                raise HTTPException(status_code=500, detail=f"Failed to send message to contact: {contact}")
    except aiohttp.ClientError as e:
            print(f"Error sending message to contact: {contact}. Error: {e}")

async def send_messages(contacts: ty.List[str], templateid: str) -> None:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=1000)) as session:
        for batch in chunks(contacts, 1000):
            tasks = [send_message(session, contact, templateid) for contact in batch]
            await asyncio.gather(*tasks)

def chunks(lst: ty.List[str], size: int) -> ty.Generator[ty.List[str], None, None]:
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

@app.post('/api/send_messages')
async def send_messages_api(templateid: str, contacts: UploadFile = File(...)) -> ty.Dict[str, str]:
    try:
        contents = await contacts.read()
        contacts = contents.decode().splitlines()
        await send_messages(contacts, templateid)
    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="Error processing the uploaded file")

    return {'Message send Successfully': 'Messages sent'}
if __name__ == '__main__':
    uvicorn.run(app)

