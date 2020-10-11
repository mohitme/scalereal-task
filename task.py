import psycopg2
from datetime import datetime
from config import config
cart = []

class Database():
    def __init__(self):
        self.params = config()
        self.conn = psycopg2.connect(**self.params)
        self.cur = self.conn.cursor()

    def sel_query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def ins_query(self, query, param):
        self.cur.execute(query, param)
        self.conn.commit()
    
    def ins_query_id(self, query, param):
        self.cur.execute(query, param)
        self.conn.commit()
        return self.cur.fetchone()[0]

    def close(self):
        self.cur.close()
        self.conn.close()


def bill():
    db = Database()
    if len(cart) == 1:
        cmd = ''' SELECT product_id,product_name,price FROM product where product_id ='''+str(cart[0])
    else:
        cmd = ''' SELECT product_id,product_name,price FROM product where product_id in {}'''.format(tuple(cart))
    rows = db.sel_query(cmd)
    print("CART")
    for row in rows:
        print("ID: "+ str(row[0]) + " Name: "+ row[1]+ " Price: "+ str(row[2]))
    inp = input("Do you want to add or remove products from cart (a for add, r for remove, c to continue): ")
    if inp == 'a':
        ls_product()
    elif inp == 'r':
        for row in rows:
            print("ID: "+ str(row[0]) + " Name: "+ row[1]+ " Price: "+ str(row[1]))
        while True:
            ind = int(input("Enter Product ID to remove (0 to continue): "))
            if ind in [i[0] for i in rows]:
                cart.remove(ind)
                print("Product Removed")
            elif ind == 0:
                break
            else:
                print("Invalid ID!!")
    elif inp == 'c':
        pass
    else:
        print("Invalid Input")
        bill()
    total = sum([i[2] for i in rows])
    fa = total if total < 10000 else total-500
    print("BILL")
    print("Actual Amount: %s" %str(total))
    print("Discounted Amount: %s" %(str(500) if total > 10000 else str(0)))
    print("Final Amount: %s" %str(fa))
    cmd = ''' INSERT into bills (bill_time,bill_amount,product_id) values (%s,%s,%s)'''
    db.ins_query(cmd,(datetime.now(),fa,[i[0] for i in rows]))
    db.close()
    exit()



def ls_product(cat=0):
    db = Database()
    if cat == 0:
        cmd = ''' SELECT product_id,product_name,price FROM product'''
    else:
        cmd = ''' SELECT product_id,product_name,price FROM product where category_id='''+str(cat)
    rows = db.sel_query(cmd)
    db.close()
    for row in rows:
        print("ID: "+ str(row[0]) + " Name: "+ row[1]+ " Price: "+ str(row[2]))
    while True:
        print("Press 0 to go bill generation")
        inp = int(input("Enter Product ID to add to cart: "))
        if inp in [i[0] for i in rows]:
            cart.append(inp)
            print("Added to cart")
        elif inp == 0:
            bill()
        else:
            print("Invalid Input!")
            continue

def ls_cat():
    db = Database()
    cmd = ''' SELECT category_id,category_name FROM category '''
    rows = db.sel_query(cmd)
    db.close()
    for row in rows:
        print("ID: "+ str(row[0]) + " Name: "+ row[1])
    cat = int(input("Select Category to show Products: "))
    if cat in [i[0] for i in rows]:
        ls_product(cat)
    else:
        print("Invalid Input")
        ls_cat()
    
def user():
    print("Welcome to MyCart")
    print("1. List Categories")
    print("2. List All Products")
    print("3. Show Cart/ Generate Bill")
    print("4. Exit")
    op = int(input("Please Select an option from above : "))
    if op == 1:
        ls_cat()
    elif op == 2:
        ls_product()
    elif op == 3:
        bill()
    elif op == 4:
        exit()
    else:
        print('Invalid Choice')
        user()

def show_bill():
    db = Database()
    cmd = ''' SELECT id,product_ids,bill_amount FROM bills '''
    rows = db.sel_query(cmd)
    
    for row in rows:
        cmd_p =  ''' SELECT product_name FROM product where product_id in {}'''.format(tuple(row[1]))
        prod = db.sel_query(cmd_p)
        print("ID: "+ str(row[0])+" Products: "+ str(prod)+" Amount: "+str(row[2]))
    db.close()

def add_cat():
    cat = input("Enter Category Name: ")
    cmd = '''INSERT into category(category_name) values (%s) RETURNING category_id '''
    db = Database()
    cat_id = db.ins_query_id(cmd,(cat,))
    print("Category Added")
    db.close()
    inp = input("Do you want to add products to this category now? (y or n): ")
    if inp == 'y':
        add_pro(cat_id)
    else:
        admin()


def add_pro(cat=0):
    db = Database()
    cmd = '''INSERT into product(product_name,price,category_id) values (%s,%s,%s) '''
    pro_name = input("Enter Product Name: ")
    pro_price = input("Enter Product Price: ")
    if cat == 0:
        cat = input("Enter Category ID for Product: ")
    db.ins_query(cmd,(pro_name,pro_price,cat))
    print("Product Added")
    db.close()

def admin():
    print("Welcome to MyCart")
    print("1. Add Categories")
    print("2. Add Products")
    print("3. Show All Bills")
    print("4. Exit")
    op = int(input("Please Select an option from above : "))
    if op == 1:
        add_cat()
    elif op == 2:
        add_pro()
    elif op == 3:
        show_bill()
    elif op == 4:
        exit()
    else:
        print('Invalid Choice')
        admin()

def main():
    #_ = os.system('cls')
    print("Welcome to MyCart")
    print("1. User")
    print("2. Admin")
    print("3. Quit")
    inp = int(input("Please Select an option from above : "))
    if inp == 1:
        user()
    elif inp == 2:
        passw = input("Enter Password: ")
        if passw == "password":
            admin()
        else:
            print("Wrong Password")
            main()
    elif inp == 3:
        exit()
    else:
        print('Invalid Choice')
        main()
    

if __name__ == "__main__":
    main()