import frappe

class sellerServices:
    def __init__(self, data):
        self.data = data
    
    def ping(self):
        return "pong"
    
    def capture_lead(self):
        return self.data
    
    
