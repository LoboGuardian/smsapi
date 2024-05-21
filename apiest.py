import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn
import httpx

app = FastAPI()

# Function to send messages to a batch of contacts
async def send_sms_batch(template_id, media_id, contact_batch):
    url = "https://automate.nexgplatforms.com/api/v1/wa/multi-send"

    data = {
        "serviceType": "transactional",
        "mediaTransid": media_id,
        "templateid": template_id,
        "fromNumber": "919711629809",
        "msgDetails": [
            {
                "messageType": "template",
                "contactnumber": contact,
                "messageid": "3fbdd0b1-030f-4359-b21c-3202f6762088",
                "dynamicUrl": "",
                "message": ""
            }
            for contact in contact_batch
        ]
    }
    headers = {
        "accept": "application/json",
        "Authorization": "cTlQLW44Mi05aFF1UEoxUmw3VGp5MGlxRFpqWkdXRXRTVHViUUk3d3VrSTo=",
        "content-type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            #response.raise_for_status()  # Raise an exception for HTTP errors
            #print(f"Messages sent: {response.text}")
        except httpx.HTTPStatusError as e:
            #print(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Failed to send messages")


# Function to divide contacts into batches and send messages
async def send_sms(template_id, media_id, contact_list, batch_size=1000):
    for i in range(0, len(contact_list), batch_size):
        contact_batch = contact_list[i:i + batch_size]
        await send_sms_batch(template_id, media_id, contact_batch)


@app.post("/send_message/")
async def message(template_id: str, media_id: str, contact_list: list[str]):
    if media_id is None:
        media_id = ""
    await send_sms(template_id, media_id, contact_list)
    return {"success": "Messages sent to all numbers"}


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.29.200", port=3000)
