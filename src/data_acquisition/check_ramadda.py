import requests

def check_ramadda():
    # In RAMADDA, entry download URL format is:
    # https://ramadda.data.bas.ac.uk/repository/entry/get/{filename}?entryid={entryid}
    # Let's inspect the entry files and their download URLs
    entry_id = "2d0e4791-8e20-46a3-80e4-f5f6716025d2"
    url = f"https://ramadda.data.bas.ac.uk/repository/entry/show?entryid={entry_id}&output=json"
    resp = requests.get(url, timeout=15)
    print("RAMADDA status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        for d in data:
            name = d.get("name")
            id_ = d.get("id")
            # Check download link
            print(f"File: {name}, ID: {id_}")

if __name__ == "__main__":
    check_ramadda()

