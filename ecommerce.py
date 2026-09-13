import json
import re
from functools import reduce

''' Customer'''

#For Regex Validation
patternEmail = r'^[\w.-]+@[\w.-]+\.com$'
patternPhone = r'^\d{11}$'
patternPassword=r'[a-zA-Z0-9]{8}'

#patternPhone=r'^01[0125]\d{8}$'

#Error Classes
class EmailError(Exception):
    def __init__(self , email):
        self.email = email
        super().__init__( f"Invalid Email:{email}")

class PhoneError(Exception):
    def __init__(self ,phone):
        self.phone = phone
        super().__init__( f"Invalid Phone Number:{phone}")
class PasswordError(Exception):
    def __init__(self ,password):
        self.password = password
        super().__init__( f"Invalid Password:{password},Must be at most 8 characters long")

#Base Class
class Customer:
    # Attributes
    def __init__(self, name, email,password, phone, level):
        self.name = name
        self.email = email
        self.password=password
        self.phone = phone
        self.level = level

        if not self.validate_email():
            raise EmailError(email)
        
        if not self.validate_phone():
            raise PhoneError(phone)
        
        if not self.validate_password():
            raise PasswordError(password)


    # Actions / Methods
    def validate_email(self):
        if re.fullmatch(patternEmail, self.email):
            return True
        return False

    def validate_phone(self):
        if re.fullmatch(patternPhone, self.phone):
            return True
        return False

    def validate_password(self):
        if re.fullmatch(patternPassword,self.password):
            return True
        return False
    

    def to_dict(self):
        return {"name":self.name,
                "email": self.email,
                "password": self.password,
                "phone": self.phone,
                "level": self.level}

    def update_level(self, order_count):
        if order_count >= 5:
            self.level = "Premium"
        return self.level

    def create_discount_engine(self): ## CLOSURE
        level = self.level
        discounts_rate=0
        usage_count=0
        def calculate_discount(total):
            nonlocal usage_count
            nonlocal discounts_rate
            if level == "Premium":
                usage_count +=1
                if usage_count<=3:
                    discounts_rate=0.10
                else:
                    discounts_rate=0.05
                return total * discounts_rate
            else:
                return discounts_rate
        return calculate_discount
    def __str__(self):
        return(f"Name: {self.name},Email: {self.email},Password:{self.password},Phone: {self.phone},Level: {self.level}")

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(data["name"],data["email"],data["password"],data["phone"],data["level"])
        except Exception as e:
            print(f"Error is:{e}")

#PremiumCustomer
class PremiumCustomer(Customer):
    def __init__(self,name, email,password, phone, premium_level):
        super().__init__(name, email,password, phone, level="Premium")
        self.premium_level = premium_level

    def get_premium(self):
        return self.level

#JSON 
class CustomerManager:
    def __init__(self):
        self.customers = []

    def find_customer(self,email):
        for customer in self.customers:
            if customer.email == email:
                return customer
            return None

    def save_to_json(self, filename="customers.json"):
        data = [c.to_dict() for c in self.customers]
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)


    def load_from_json(self, filename="customers.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            self.customers = [Customer.from_dict(item) for item in data]

        except FileNotFoundError:
            #If the file not existed, make new one
            self.customers = []
            self.save_to_json(filename)  
            print(f"File:{filename} is not found,Made a new one")

        except json.JSONDecodeError:
            # if the JSON is existed but is enpty or dameged
            self.customers = []
            print(f"File: {filename} is empty or dameged, Made a new one")



''' Products'''


class ProductCodeError(Exception):
    def __init__(self , code):
        self.code = code
        super().__init__(f"Invalid product code:{code}")

class ProductAlreadyExistsError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(f"Product with code {code} already exists")

class ProductNotFoundError(Exception):
    def __init__(self,code):
        self.code = code
        super().__init__(f"Product with code {code} not found.")

class StockError(Exception):
    def __init__(self , product_name , requested , available):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(f"No enough stock, the requsted: {self.requested},The avilable :{self.available}")

class PriceError(Exception):
    def __init__(self, price):
        self.price = price
        super().__init__(f"invalid price:{self.price}") 

class QuantityError(Exception):
    def __init__(self, quantity):
        self.quantity = quantity
        super().__init__(f"Invalid quantity: {quantity}")

# base class
class Product:
    def __init__(self , code , name , price , stock , product_type):
        self.validate_product_code(code)
        self.validate_product_price(price)
        self.validate_stock(stock)

        self.code = code
        self.name = name
        self.price = price
        self.stock = stock
        self.product_type = product_type

    def get_description(self):
        return f'Name:{self.name},Type:{self.product_type} ,Price:{self.price}'
   
    def reduce_stock(self , quantity):
        if quantity <=0:
            raise QuantityError(quantity)
        if quantity > self.stock:
            raise StockError(self.name , quantity , self.stock)

        self.stock -= quantity

    def is_available(self , quantity = 1):
        return quantity>0 and self.stock>=quantity    
         
    def is_low_stock(self , threshold = 5):
        return self.stock<=threshold

    def validate_product_code(self ,code):
        patternProductCode=r"^[PDS]\d{5}$"
        if re.fullmatch(patternProductCode,code):
            return True
        else:
            raise ProductCodeError(code)

    def validate_product_price(self , price):
        if isinstance(price,(int,float)) and price >0:
            return True
        else:
            raise PriceError(price) 
         
    def validate_stock(self,stock):
        if isinstance(stock,int) and stock>=0:
            return True
        else:
             raise ValueError("Invalid stock")
            
    #Caluclate Total price of the certain product 
    def calculate_total(self , quantity):
        if quantity<=0:
            raise QuantityError(quantity)
        return self.price * quantity
    
    def to_dict(self):
        return { "code": self.code, "name": self.name,
                "price": self.price, "stock": self.stock, "product_type": self.product_type}

#Subclasses

#Physical Products
class PhysicalProduct(Product):
    def __init__(self , code , name , price , stock, weight):
        super().__init__(code , name , price , stock,product_type="Physical")
        self.weight = weight
        #self.shipping_cost=shipping_cost

    def calculate_shipping(self):
        return self.weight * 15

    def get_description(self):
        shipping=self.calculate_shipping()
        return f"[{self.code}] {self.name} - ${self.price} (Physical, Weight: {self.weight}kg, Shipping: ${shipping})"

    def to_dict(self):
        data=super().to_dict()
        data.update({"weight":self.weight})
        return data
        #return { "code": self.code, "name": self.name,"price": self.price,"stock": self.stock, "type": self.product_type,"weight":self.weight}

#Digital Products
class DigitalProduct(Product):
    def __init__(self , code , name , price , stock, download_link):
        super().__init__(code , name , price , stock,product_type="Digital")
        self.download_link = download_link

    def get_description(self):
        return f"[{self.code}] {self.name} - ${self.price} (Digital, Instant Download, No Shipping)"

    def to_dict(self):
        data=super().to_dict()
        data.update({"download_link":self.download_link})
        return data
        #return { "code": self.code, "name": self.name,"price": self.price,"stock": self.stock, "type": self.product_type,"download link":self.download_link}
    
    def get_download_link(self):
        return self.download_link    

#Service
class Service(Product):
    def __init__(self , code , name , price , stock, duration, provider):
        super().__init__(code , name , price , stock,product_type="Service")
        self.duration = duration
        self.provider=provider
    def get_description(self):
        return f"[{self.code}] {self.name} - ${self.price} (Service, Duration: {self.duration} hrs, Provider:{self.provider})"

    def to_dict(self):
        data=super().to_dict()
        data.update({"duration":self.duration,"provider":self.provider})
        return data
    
    def is_long_service(self):
        return self.duration > 3

# Product Manging(add,find,delete,get_all_product)     
class ProductManager():
    def __init__(self):
        self.products=[]
    def find_product(self,code):
        for product in self.products:
            if product.code ==code:
                return product
        return None
    
    def add_product(self,product):
        if self.find_product(product.code) is not None:
            raise ProductAlreadyExistsError(product.code)
        
        self.products.append(product)
        return product

    def delete_product(self,code):
        product=self.find_product(code)
        if product is None:
            raise ProductNotFoundError(code)
        else:
            self.products.remove(product)
            return True
        
    def get_all_products(self):
        return list(self.products)
        
    def __iter__(self):
        return iter(self.products)
    def __len__(self):
        return len(self.products)

    def low_stock_products(self, limit = 5):
        return list(filter(lambda x: x.is_low_stock(limit),self.products))

    def sort_by_price(self, descending: bool = False):
        return sorted(self.products, key=lambda x: x.price,reverse=descending)

    def list_product_names(self):
        return list(map(lambda x: x.name, self.products))
    
    def update_stock(self, code, new_stock):
        product = self.find_product(code)
        if product is None:
            raise ProductNotFoundError(code)
        product.validate_stock(new_stock)
        product.stock = new_stock
#JSON 
    def save_to_json(self, filename="products.json"):
        data = [p.to_dict() for p in self.products]
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

            
    def load_from_json(self, filename="products.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)

            self.products = []
            for item in data:
                if item["product_type"] == "Physical":
                    p = PhysicalProduct(item["code"], item["name"], item["price"],
                                        item["stock"], item["weight"])
                elif item["product_type"] == "Digital":
                    p = DigitalProduct(item["code"], item["name"], item["price"],
                                        item["stock"], item["download_link"])
                elif item["product_type"] == "Service":
                    p = Service(item["code"], item["name"], item["price"],
                                item["stock"], item["duration"], item["provider"])
                self.products.append(p)

        except FileNotFoundError:
            #If the file not existed, make new one
            self.products = []
            self.save_to_json(filename)  
            print(f"File:{filename} is not found,Made a new one")

        except json.JSONDecodeError:
            # if the JSON is existed but is enpty or dameged
            self.products = []
            print(f"File: {filename} is empty or dameged, Made a new one")



''' Cart & Order'''

#Exception Calsses
class OrderCodeError(Exception):
    def __init__(self,order_id):
        self.order_id=order_id
        super().__init__(f"Order ID:{order_id} is invalid")

class OrderNotFoundError(Exception):
    def __init__(self,order_id):
        self.order_id=order_id
        super().__init__(f"Order Code:{order_id} not found")

class OrderCancellationError(Exception):
    def __init__(self,status):
        self.status=status
        super().__init__(f"Can't Cancel when the status is:{status}")

class InvalidStatusError(Exception):
    def __init__(self,status):
        self.status=status
        super().__init__(f"Invalid Status: {status}")


#Cart Class
class Cart:
    def __init__(self,customer_email):
        #self.customer_id=customer_id
        self.customer_email=customer_email
        self.items = []

    def add_product(self, product, quantity):
        if quantity <= 0:
            raise QuantityError(quantity)
        # if quantity > product.stock:
        #     raise ValueError("Not enough stock")
        if not product.is_available(quantity):
            raise StockError(product.name,quantity,product.stock)
        
        for item in self.items:
            if item["product"].code == product.code:
                new_quantity = item["quantity"] + quantity

                if new_quantity > product.stock:
                    raise StockError(product.name,new_quantity,product.stock)
                item["quantity"] = new_quantity
                return
        self.items.append({"product": product,"quantity": quantity})

    def remove_product(self, product_code):
        for item in self.items:
            if item["product"].code == product_code:
                self.items.remove(item)
                return True
        raise ProductCodeError(product_code)
        
    def update_quantity(self,product_code,new_quantity):
        if new_quantity<=0:
            raise QuantityError(new_quantity)
        for item in self.items:
            if item["product"].code == product_code:
                product=item["product"]
                
                if not product.is_available(new_quantity):
                    raise StockError(product.name,new_quantity,product.stock)
                item["quantity"]=new_quantity
                return True
        raise ProductCodeError(product_code)

    def calculate_total(self):
        total = reduce(lambda total,
                       item: total + item["product"].price * item["quantity"],self.items,0)
        return total

    
    def clear(self):
        self.items=[]
    def is_empty(self):
        return not self.items


class ProductCodeError(Exception):
    def __init__(self , code):
        self.code = code
        super().__init__(f"Invalid product code:{code}")

class ProductAlreadyExistsError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(f"Product with code {code} already exists")

class ProductNotFoundError(Exception):
    def __init__(self,code):
        self.code = code
        super().__init__(f"Product with code {code} not found.")

class StockError(Exception):
    def __init__(self , product_name , requested , available):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(f"No enough stock, the requsted: {self.requested},The avilable :{self.available}")

class PriceError(Exception):
    def __init__(self, price):
        self.price = price
        super().__init__(f"invalid price:{self.price}") 

class QuantityError(Exception):
    def __init__(self, quantity):
        self.quantity = quantity
        super().__init__(f"Invalid quantity: {quantity}")

# base class
class Product:
    def __init__(self , code , name , price , stock , product_type):
        self.validate_product_code(code)
        self.validate_product_price(price)
        self.validate_stock(stock)

        self.code = code
        self.name = name
        self.price = price
        self.stock = stock
        self.product_type = product_type

    def get_description(self):
        return f'Name:{self.name},Type:{self.product_type} ,Price:{self.price}'
   
    def reduce_stock(self , quantity):
        if quantity <=0:
            raise QuantityError(quantity)
        if quantity > self.stock:
            raise StockError(self.name , quantity , self.stock)

        self.stock -= quantity

    def is_available(self , quantity = 1):
        return quantity>0 and self.stock>=quantity    
         
    def is_low_stock(self , threshold = 5):
        return self.stock<=threshold

    def validate_product_code(self ,code):
        patternProductCode=r"^[PDS]\d{5}$"
        if re.fullmatch(patternProductCode,code):
            return True
        else:
            raise ProductCodeError(code)

    def validate_product_price(self , price):
        if isinstance(price,(int,float)) and price >0:
            return True
        else:
            raise PriceError(price) 
         
    def validate_stock(self,stock):
        if isinstance(stock,int) and stock>=0:
            return True
        else:
             raise ValueError("Invalid stock")
            
    #Caluclate Total price of the certain product 
    def calculate_total(self , quantity):
        if quantity<=0:
            raise QuantityError(quantity)
        return self.price * quantity
    
    def to_dict(self):
        return { "code": self.code, "name": self.name,
                "price": self.price, "stock": self.stock, "product_type": self.product_type}

#Subclasses

#Physical Products
class PhysicalProduct(Product):
    def __init__(self , code , name , price , stock, weight):
        super().__init__(code , name , price , stock,product_type="Physical")
        self.weight = weight
        #self.shipping_cost=shipping_cost

    def calculate_shipping(self):
        return self.weight * 15

    def get_description(self):
        shipping=self.calculate_shipping()
        return f"[{self.code}] {self.name} - ${self.price} (Physical, Weight: {self.weight}kg, Shipping: ${shipping})"

    def to_dict(self):
        data=super().to_dict()
        data.update({"weight":self.weight})
        return data
        #return { "code": self.code, "name": self.name,"price": self.price,"stock": self.stock, "type": self.product_type,"weight":self.weight}

#Digital Products
class DigitalProduct(Product):
    def __init__(self , code , name , price , stock, download_link):
        super().__init__(code , name , price , stock,product_type="Digital")
        self.download_link = download_link

    def get_description(self):
        return f"[{self.code}] {self.name} - ${self.price} (Digital, Instant Download, No Shipping)"

    def to_dict(self):
        data=super().to_dict()
        data.update({"download_link":self.download_link})
        return data
        #return { "code": self.code, "name": self.name,"price": self.price,"stock": self.stock, "type": self.product_type,"download link":self.download_link}
    
    def get_download_link(self):
        return self.download_link    

#Service
class Service(Product):
    def __init__(self , code , name , price , stock, duration, provider):
        super().__init__(code , name , price , stock,product_type="Service")
        self.duration = duration
        self.provider=provider
    def get_description(self):
        return f"[{self.code}] {self.name} - ${self.price} (Service, Duration: {self.duration} hrs, Provider:{self.provider})"

    def to_dict(self):
        data=super().to_dict()
        data.update({"duration":self.duration,"provider":self.provider})
        return data
    
    def is_long_service(self):
        return self.duration > 3

# Product Manging(add,find,delete,get_all_product)     
class ProductManager():
    def __init__(self):
        self.products=[]
    def find_product(self,code):
        for product in self.products:
            if product.code ==code:
                return product
        return None
    
    def add_product(self,product):
        if self.find_product(product.code) is not None:
            raise ProductAlreadyExistsError(product.code)
        
        self.products.append(product)
        return product

    def delete_product(self,code):
        product=self.find_product(code)
        if product is None:
            raise ProductNotFoundError(code)
        else:
            self.products.remove(product)
            return True
        
    def get_all_products(self):
        return list(self.products)
        
    def __iter__(self):
        return iter(self.products)
    def __len__(self):
        return len(self.products)

    def low_stock_products(self, limit = 5):
        return list(filter(lambda x: x.is_low_stock(limit),self.products))

    def sort_by_price(self, descending: bool = False):
        return sorted(self.products, key=lambda x: x.price,reverse=descending)

    def list_product_names(self):
        return list(map(lambda x: x.name, self.products))
    
    def update_stock(self, code, new_stock):
        product = self.find_product(code)
        if product is None:
            raise ProductNotFoundError(code)
        product.validate_stock(new_stock)
        product.stock = new_stock

    #JSON 
    def save_to_json(self, filename="products.json"):
        data = [p.to_dict() for p in self.products]
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
            
    def load_from_json(self, filename="products.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)

            self.products = []
            for item in data:
                if item["product_type"] == "Physical":
                    p = PhysicalProduct(item["code"], item["name"], item["price"],
                                        item["stock"], item["weight"])
                elif item["product_type"] == "Digital":
                    p = DigitalProduct(item["code"], item["name"], item["price"],
                                        item["stock"], item["download_link"])
                elif item["product_type"] == "Service":
                    p = Service(item["code"], item["name"], item["price"],
                                item["stock"], item["duration"], item["provider"])
                self.products.append(p)

        except FileNotFoundError:
            #If the file not existed, make new one
            self.products = []
            self.save_to_json(filename)  
            print(f"File:{filename} is not found,Made a new one")

        except json.JSONDecodeError:
            # if the JSON is existed but is enpty or dameged
            self.products = []
            print(f"File: {filename} is empty or dameged, Made a new one")

def seed_initial_products(product_manager):
    if len(product_manager) > 0:
        return  
    starter_products = [
        PhysicalProduct("P00001", "Wireless Mouse", 250, 30, weight=0.3),
        PhysicalProduct("P00002", "Mechanical Keyboard", 950, 15, weight=1.1),
        DigitalProduct("D00001", "Python Programming E-Book", 150, 999, download_link="example.com/pybook"),
        DigitalProduct("D00002", "Photo Editing Software License", 400, 500, download_link="example.com/editpro"),
        Service("S00001", "Laptop Repair Service", 300, 10, duration=2, provider="TechFix Center"),
        Service("S00002", "1-on-1 Programming Tutoring", 200, 20, duration=1, provider="CodeMentor"),
    ]
    for p in starter_products:
        product_manager.add_product(p)
    product_manager.save_to_json()


"""Orders"""
#Order Class
#Exception Calsses
class OrderCodeError(Exception):
    def __init__(self,order_id):
        self.order_id=order_id
        super().__init__(f"Order ID:{order_id} is invalid")

class OrderNotFoundError(Exception):
    def __init__(self,order_id):
        self.order_id=order_id
        super().__init__(f"Order Code:{order_id} not found")

class OrderCancellationError(Exception):
    def __init__(self,status):
        self.status=status
        super().__init__(f"Can't Cancel when the status is:{status}")

class InvalidStatusError(Exception):
    def __init__(self,status):
        self.status=status
        super().__init__(f"Invalid Status: {status}")

#Cart Class
class Cart:
    def __init__(self,customer_email):
        #self.customer_id=customer_id
        self.customer_email=customer_email
        self.items = []

    def add_product(self, product, quantity):
        if quantity <= 0:
            raise QuantityError(quantity)
        # if quantity > product.stock:
        #     raise ValueError("Not enough stock")
        if not product.is_available(quantity):
            raise StockError(product.name,quantity,product.stock)
        
        for item in self.items:
            if item["product"].code == product.code:
                new_quantity = item["quantity"] + quantity

                if new_quantity > product.stock:
                    raise StockError(product.name,new_quantity,product.stock)
                item["quantity"] = new_quantity
                return
        self.items.append({"product": product,"quantity": quantity})

    def remove_product(self, product_code):
        for item in self.items:
            if item["product"].code == product_code:
                self.items.remove(item)
                return True
        raise ProductCodeError(product_code)
        
    def update_quantity(self,product_code,new_quantity):
        if new_quantity<=0:
            raise QuantityError(new_quantity)
        for item in self.items:
            if item["product"].code == product_code:
                product=item["product"]
                
                if not product.is_available(new_quantity):
                    raise StockError(product.name,new_quantity,product.stock)
                item["quantity"]=new_quantity
                return True
        raise ProductCodeError(product_code)

    def calculate_total(self):
        total = reduce(lambda total,
                       item: total + item["product"].price * item["quantity"],self.items,0)
        return total

    
    def clear(self):
        self.items=[]
    def is_empty(self):
        return not self.items


#Order Class
class Order:
    def __init__(self,order_id,customer_email,items,total,discount,final_total):
        self.validate_order_id(order_id)
        self.order_id=order_id
        self.customer_email=customer_email
        self.items = items
        self.total= total
        self.discount=discount
        self.final_total=final_total
        self.status = "Pending"

    def validate_order_id(self,order_id):
        patternOrderID = r"^ORD\d{3}$"
        if re.fullmatch(patternOrderID,order_id):
            return True
        raise OrderCodeError(order_id)
    
    def update_status(self, new_status):
        valid_statuses = ["Pending","Processing","Shipped",
                          "Delivered","Cancelled"]
        
        if new_status not in valid_statuses:
            raise InvalidStatusError(new_status)
        if new_status == "Cancelled" and self.status in ["Shipped","Delivered"]:
            raise OrderCancellationError(self.status)
        
        self.status = new_status

    def cancel_order(self):
        self.update_status("Cancelled")

    def to_dict(self):
        return {"order_id":self.order_id,
                "customer_email":self.customer_email,
                "items":[{"code":i["product"].code,"quantity":i["quantity"]} for i in self.items],
                "total": self.total,"discount": self.discount,
                "final_total": self.final_total,
                "status":self.status}


#OrderManager Class
class OrderManager:
    def __init__(self):
        self.orders = []
        self.next_id = 1

    def checkout(self, cart,customer):
        if cart.is_empty():
            raise ValueError("Cannot checkout an empty cart")
        #Only Checking
        for item in cart.items:
            product = item["product"]
            quantity = item["quantity"]   
            if not product.is_available(quantity):
                raise StockError(product.name,quantity,product.stock)

        total = cart.calculate_total()
        discount = customer.create_discount_engine()(total)
        final_total=total-discount

        #Take the action
        for item in cart.items:
            product = item["product"]
            quantity = item["quantity"] 
            product.reduce_stock(quantity)

        #Create Order ID
        order_id = f"ORD{self.next_id:03d}"
        #Copy Cart Items
        order_items=list(cart.items)
        order = Order(order_id,cart.customer_email,order_items,total,discount,final_total)
        self.orders.append(order)

        customer_orders = self.get_orders_by_customer(cart.customer_email)
        customer.update_level(len(customer_orders))

        self.next_id += 1
        cart.clear()
        return order
    
    def find_order(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        raise OrderNotFoundError(order_id)
    
    def update_status(self, order_id, new_status):
        order = self.find_order(order_id)
        order.update_status(new_status)
        return order
    
    def get_all_orders(self):
        return list(self.orders)

    def get_orders_by_customer(self, customer_email):
        return [order for order in self.orders if order.customer_email == customer_email]


    #JSON
    def save_to_json(self, filename="orders.json"):
        data = [o.to_dict() for o in self.orders]
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)

def load_orders_from_json(order_manager, product_manager, filename="orders.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        order_manager.orders = []
        max_id = 0
        for item in data:
            items = []
            for i in item["items"]:
                product = product_manager.find_product(i["code"])
                if product is not None:
                    items.append({"product": product, "quantity": i["quantity"]})
            order = Order(item["order_id"], item["customer_email"], items,
                        item["total"], item["discount"], item["final_total"])
            order.status = item["status"]
            order_manager.orders.append(order)
            num = int(item["order_id"].replace("ORD", ""))
            max_id = max(max_id, num)
        order_manager.next_id = max_id + 1
    except FileNotFoundError:
        order_manager.orders = []
        order_manager.save_to_json(filename)
        print(f"File:{filename} not found, Made a new one")
    except json.JSONDecodeError:
        order_manager.orders = []
        print(f"File:{filename} is empty or damaged, starting fresh")

''' Reports'''

def sales_report(order_manager):
    completed=list(filter(lambda o:o.status!="Cancelled",order_manager.orders))
    total_sales=reduce(lambda acc,o: acc+o.final_total,completed,0)
    return{"total_orders":len(completed),"total_sales":total_sales}

def low_stock_report(product_manager,threshold=5):
    return product_manager.low_stock_products(threshold)

#Show only top 3 selling products
def top_products_report(order_manager,top_num=3):
    counter={}
    for order in order_manager.orders:
        for item in order.items:
            code = item["product"].code
            counter[code] = counter.get(code, 0) + item["quantity"]
    return sorted(counter.items(), key=lambda x: x[1], reverse=True) [:top_num]


"""Authentication"""

class AuthenticationError(Exception):
    def __init__(self,message="Invalid credentials"):
        super().__init__(message)

ADMIN_EMAIL = "admin@store.com"
ADMIN_PASSWORD = "AdminPass"

class AuthManager:
    def __init__(self, customer_manager, admin_email=ADMIN_EMAIL,admin_password=ADMIN_PASSWORD):
        self.customer_manager = customer_manager
        self.admin_email = admin_email
        self.admin_password=admin_password

    def register(self, name, email, password, phone):
        if self.customer_manager.find_customer(email) is not None:
            raise ValueError(f"Email:{email} is already existed")
        new_customer = Customer(name, email, password, phone, level="Regular")
        self.customer_manager.customers.append(new_customer)
        self.customer_manager.save_to_json()
        return new_customer
 
    def login_customer(self, email, password):
        customer = self.customer_manager.find_customer(email)
        if customer is None or customer.password != password:
            raise AuthenticationError("Invalid email or password")
        return customer
 
    def login_admin(self, email,password):
        if email != self.admin_email or password != self.admin_password:
            raise AuthenticationError("Invalid admin email or password")
        return True




'''Main'''
def print_products(product_manager):
    if len(product_manager) == 0:
        print("No products are currently available.")
        return
    print("\n--- Available Products ---")
    for p in product_manager.get_all_products():
        stock_note = "  (Low stock!)" if p.is_low_stock() else ""
        print(f"{p.get_description()} | In stock: {p.stock}{stock_note}")
 
def browse_products_menu(product_manager, cart):
    while True:
        print_products(product_manager)
        print("\n1. Add a product to cart")
        print("0. Back to main menu")
        choice = input("Choose: ").strip()
 
        if choice == "0":
            return
        elif choice == "1":
            if cart is None:
                print("You need to log in first to add items to a cart (choose 2 from the main menu).")
                continue
            code = input("Product code: ").strip().upper()
            product = product_manager.find_product(code)
            if product is None:
                print(f"No product found with code {code}")
                continue
            try:
                qty = int(input("Quantity: "))
                cart.add_product(product, qty)
                print("Added to cart successfully.")
            except (QuantityError, StockError) as error:
                print(f"Error: {error}")
            except ValueError:
                print("Quantity must be a valid integer.")
        else:
            print("Invalid choice.")
 
 
def register_or_login_menu(auth_manager, order_manager,product_manager):

    while True:
        print("\n--- Register / Login ---")
        print("1. Create a new account (Register)")
        print("2. Log in")
        print("0. Back to main menu")
        choice = input("Choose: ").strip()
 
        if choice == "0":
            return None
 
        elif choice == "1":
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            phone = input("Phone number (11 digits): ").strip()
            try:
                customer = auth_manager.register(name, email, password, phone)
                print(f"Account created successfully. Welcome, {customer.name}!")
                return customer_account_menu(customer, order_manager)
            except (EmailError, PhoneError,PasswordError, ValueError) as error:
                print(f"Error: {error}")
 
        elif choice == "2":
            email = input("Email: ").strip()
            password = input("Password: ").strip()

            if email == ADMIN_EMAIL:
                try:
                    auth_manager.login_admin(email, password)
                    print("Logged in as admin.")
                    admin_menu(product_manager, order_manager)   
                    return None   
                except AuthenticationError as error:
                    print(f"Error: {error}")
                continue
            try:
                customer = auth_manager.login_customer(email, password)
                print(f"Welcome back, {customer.name}!")
                return customer_account_menu(customer, order_manager)
            except AuthenticationError as error:
                print(f"Error: {error}")
        else:
            print("Invalid choice.")
 
 
def customer_account_menu(customer, order_manager):
    """
    Customer's account menu after logging in — view and cancel orders.
    Returns the customer object so the main loop keeps them logged in.
    """
    while True:
        print(f"\n--- {customer.name}'s Account ({customer.level}) ---")
        print("1. View my orders")
        print("2. Cancel an order")
        print("0. Back (stays logged in)")
        choice = input("Choose: ").strip()
 
        if choice == "0":
            return customer
 
        elif choice == "1":
            orders = order_manager.get_orders_by_customer(customer.email)
            if not orders:
                print("You have no orders yet.")
            for o in orders:
                print(f"Order ID: {o.order_id} | Total: {o.final_total} | Status: {o.status}")
 
        elif choice == "2":
            order_id = input("Order ID to cancel: ").strip().upper()
            try:
                order = order_manager.find_order(order_id)
            except OrderNotFoundError as error:
                print(f"Error:{error}")
                continue
            if order is None or order.customer_email != customer.email:
                print("No order with that ID was found in your account.")
                continue
            if order.status not in ["Pending", "Processing"]:
                print(f"Cannot cancel an order in status {order.status}.")
                continue
            try:
                order.cancel_order()
                order_manager.save_to_json()
                print("Order cancelled successfully.")
            except OrderCancellationError as error:
                print(f"Error: {error}")

        else:
            print("Invalid choice.")
 
 
def cart_checkout_menu(current_customer, cart, order_manager, customer_manager):
    if current_customer is None:
        print("You need to log in first (choose 2 from the main menu).")
        return
 
    while True:
        if cart.is_empty():
            print("\nYour cart is currently empty.")
        else:
            print("\n--- Your Cart ---")
            for item in cart.items:
                p = item["product"]
                print(f"[{p.code}] {p.name} x {item['quantity']} = {p.price * item['quantity']}")
                print(f"Total: {cart.calculate_total()}")

 
        print("\n1. Checkout")
        print("2. Remove a product from cart")
        print("0. Back to main menu")
        choice = input("Choose: ").strip()
 
        if choice == "0":
            return
        elif choice == "1":
            try:
                order = order_manager.checkout(cart, current_customer)
                order_manager.save_to_json()
                customer_manager.save_to_json()
                print(f"Order placed successfully! Order ID: {order.order_id}, Final total after discount: {order.final_total}")
            except (StockError, ValueError, QuantityError) as error:
                print(f"Error: {error}")
        elif choice == "2":
            code = input("Product code to remove: ").strip().upper()
            try:
                cart.remove_product(code)
                print("Removed from cart.")
            except ProductCodeError as error:
                print(f"Error: {error}")
        else:
            print("Invalid choice.")
 
 
def admin_menu(product_manager, order_manager):
    while True:
        print("\n--- Admin Dashboard ---")
        print("1. Sales report")
        print("2. Low stock report")
        print("3. Top-selling products")
        print("4. Add a new product")
        print("5. Delete a product")
        print("6. Update a product's stock")
        print("7. View all orders and update their status")
        print("0. Back to main menu")
        choice = input("Choose: ").strip()
 
        if choice == "0":
            return
 
        elif choice == "1":
            report = sales_report(order_manager)
            print(f"Total orders: {report['total_orders']} | Total sales: {report['total_sales']}")
 
        elif choice == "2":
            low_stock = low_stock_report(product_manager)
            if not low_stock:
                print("No products are currently low on stock.")
            for p in low_stock:
                print(f"{p.name} ({p.code}) - Remaining: {p.stock}")
 
        elif choice == "3":
            top = top_products_report(order_manager)
            if not top:
                print("Not enough sales data yet.")
            for code, qty in top:
                print(f"{code}: sold {qty} units")
 
        elif choice == "4":
            add_product_flow(product_manager)
 
        elif choice == "5":
            code = input("Product code to delete: ").strip().upper()
            try:
                product_manager.delete_product(code)
                product_manager.save_to_json()
                print("Product deleted.")
            except ProductNotFoundError as error:
                print(f"Error: {error}")
 
        elif choice == "6":
            code = input("Product code: ").strip().upper()
            try:
                new_stock = int(input("New stock quantity: "))
                product_manager.update_stock(code, new_stock)
                product_manager.save_to_json()
                print("Stock updated.")
            except ProductNotFoundError as error:
                print(f"Error: {error}")
            except ValueError:
                print("Stock must be a valid integer.")
 
        elif choice == "7":
            admin_orders_menu(order_manager)
 
        else:
            print("Invalid choice.")
 
def add_product_flow(product_manager):
    print("\nProduct type: 1.Physical  2.Digital  3.Service")
    ptype = input("Choose: ").strip().lower()
    code = input("Product code (format: P/D/S + 5 digits, e.g. P00003): ").strip().upper()
    name = input("Name: ").strip().lower()
    try:
        price = float(input("Price: "))
        stock = int(input("Stock quantity: "))
 
        if ptype == "1":
            weight = float(input("Weight (kg): "))
            product = PhysicalProduct(code, name, price, stock, weight)
        elif ptype == "2":
            link = input("Download link: ").strip()
            product = DigitalProduct(code, name, price, stock, link)
        elif ptype == "3":
            duration = float(input("Service duration (hours): "))
            provider = input("Provider: ").strip()
            product = Service(code, name, price, stock, duration, provider)
        else:
            print("Invalid product type.")
            return
 
        product_manager.add_product(product)
        product_manager.save_to_json()
        print("Product added successfully.")
 
    except (ProductCodeError, PriceError, ValueError, ProductAlreadyExistsError) as error:
        print(f"Error: {error}")
 
 
def admin_orders_menu(order_manager):
    orders = order_manager.get_all_orders()
    if not orders:
        print("No orders yet.")
        return
    for o in orders:
        print(f"{o.order_id} | {o.customer_email} | Status: {o.status} | Total: {o.final_total}")
 
    order_id = input("\nOrder ID to update status (or 0 to go back): ").strip()
    if order_id == "0":
        return
    print("Available statuses: Pending, Processing, Shipped, Delivered, Cancelled")
    new_status = input("New status: ").strip()
    try:
        order_manager.update_status(order_id, new_status)
        order_manager.save_to_json()
        print("Order status updated.")
    except (OrderNotFoundError, InvalidStatusError, OrderCancellationError) as error:
        print(f"Error: {error}")
 
 
def admin_login_flow(auth_manager, product_manager, order_manager):
    code = input("Enter admin code: ").strip().upper()
    try:
        auth_manager.login_admin(code)
        print("Logged in as admin.")
        admin_menu(product_manager, order_manager)
    except AuthenticationError as error:
        print(f"Error: {error}")
 
 
def main():
    product_manager = ProductManager()
    customer_manager = CustomerManager()
    order_manager = OrderManager()
 
    product_manager.load_from_json()
    seed_initial_products(product_manager)  # adds starter products if the file was empty
    customer_manager.load_from_json()
    load_orders_from_json(order_manager, product_manager)
 
    auth_manager = AuthManager(customer_manager)
 
    current_customer = None
    cart = None
 
    while True:
        print("\n===== Mini E-commerce Store =====")
        print("1. Browse Products")
        print("2. Register/Login" + (f"  (logged in as {current_customer.name})" if current_customer else ""))
        print("3. View Cart/Checkout")
        print("0. Exit")
        choice = input("Choose: ").strip()
 
        if choice == "0":
            product_manager.save_to_json()
            customer_manager.save_to_json()
            order_manager.save_to_json()
            print("All data saved. Goodbye!")
            break
 
        elif choice == "1":
            browse_products_menu(product_manager, cart)
 
        elif choice == "2":
            result = register_or_login_menu(auth_manager, order_manager, product_manager)
            if result is not None:
                current_customer = result
                if cart is None:
                    cart = Cart(current_customer.email)
 
        elif choice == "3":
            if cart is None:
                cart = Cart(current_customer.email) if current_customer else None
            cart_checkout_menu(current_customer, cart, order_manager, customer_manager)
 
        else:
            print("Invalid choice, please try again.")
 
 
main()
