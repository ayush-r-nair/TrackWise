import os
import json
import requests
import datetime as dt

class OCR_SCAN():
    def __init__(self):
        self.API_KEY="TEST" 
        self.url="https://ocr2.asprise.com/api/v1/receipt"
        self.IMAGES_DIR="images"
        self.OUTPUT_DIR="outputs/expenses.json"
        
        if os.path.exists(self.OUTPUT_DIR):
            with open(self.OUTPUT_DIR,"r") as f:
                self.expenses=json.load(f)
        else :
            self.expenses=[]
    
    def scan_image(self,path):
        with open(path,"rb") as f:
            response = requests.post(
                self.url, 
                data = {
                    'api_key': self.API_KEY,        
                    'recognizer': 'auto',     
                    'ref_no': 'ocr_python_123'
                },
                files = {"file": f}
            )
        
        if(response.status_code!=200) :
            return None
        
        data=response.json()
        return data


    def extract_fields(self,data,path):     
        receipt_data=data["receipts"][0]
        
        return {
            "id": dt.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "image_file": path,
            "merchant": receipt_data.get("merchant_name", "Unknown"),
            "date": receipt_data.get("date", None),
            "time": receipt_data.get("time", None),
            "total": receipt_data.get("total", None),
            "subtotal": receipt_data.get("subtotal", None),
            "tax": receipt_data.get("tax", None),
            "items": receipt_data.get("items", []),
            "scanned_at": dt.datetime.now().isoformat()
        }
    
    
    def process_all(self):
        files = [
            f for f in os.listdir(self.IMAGES_DIR)
        ]

        print(f"Found {len(files)} receipts in folder.")

        for file in files:
            if any(r["image_file"] == file for r in self.expenses):
                print(f"Skipping {file} (already processed).")
                continue

            print(f"Scanning → {file}")
            full_path = os.path.join(self.IMAGES_DIR, file)

            result = self.scan_image(full_path)

            if not result or "receipts" not in result or len(result["receipts"]) == 0:
                print(f"Could NOT extract data from: {file}")
                continue

            structured  = self.extract_fields(result, file)
            self.expenses.append(structured)

            with open(self.OUTPUT_DIR, "w") as f:
                json.dump(self.expenses, f, indent=2)

            print(f"Saved: {structured['merchant']} - {structured['total']}")

        print("\n----- Processing complete -----")
        print(f"Total receipts processed: {len(self.expenses)}")

    
    def show_summary(self):
        print("\n===== SUMMARY =====\n")
        print(f"Total receipts: {len(self.expenses)}")

        total_spent = sum(e.get("total", 0) for e in self.expenses if e.get("total"))
        print(f"Total spent: ₹{total_spent:.2f}\n")

        print("Last few receipts:\n")
        for e in self.expenses[-5:]:
            print(f"{e['merchant']} - ₹{e['total']} - {e['image_file']}")


if __name__=="__main__":
    scanner=OCR_SCAN()
    scanner.process_all()
    scanner.show_summary()