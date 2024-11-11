from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.p
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    download_order_file()
    create_orders_with_order_data()
    archive_receipts()
   


def open_robot_order_website():
    """Navigates to the website to order robots"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_order_file():
    """Downloads the files from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def create_orders_with_order_data():
    """Read the data from the downloaded file"""
    orders = Tables()
    worksheet = orders.read_table_from_csv("orders.csv", header=True)

    for row in worksheet:
       fill_and_submit_orders(row)
        
        


def close_annoying_modal():
    """Closing the modal with const"""
    page = browser.page()
    page.click("text=I guess so...")

def fill_and_submit_orders(row):
    """Fill the orders from the downloaded order file"""
    page = browser.page()

    close_annoying_modal()
    
    body_value = str(row["Body"])

    page.select_option("#head", str(row["Head"]))
    page.check(f"#id-body-{body_value}")
    page.fill("input[type='number']", str(row["Legs"]))
    page.fill("#address", str(row["Address"]))
    page.click("#preview")
    
    max_retries = 5
    attempts = 0
    order_successful = False

    while attempts < max_retries and not order_successful:
        page.wait_for_selector("#order:enabled", timeout=1000)
        page.click("#order")


        try:
            page.wait_for_selector("#receipt", timeout=1000)
            order_number = page.query_selector(".badge-success").inner_text()
            pdf_file = store_receipt_as_pdf(order_number)
            screenshot = screenshot_robot(order_number)
            embed_screenshot_to_receipt(screenshot, pdf_file)
            order_successful = True
           
  
        except:
            error_message = page.query_selector(".alert-danger")

            if error_message:
                attempts += 1
                page.wait_for_timeout(1000) 
            else:
                break

    if not order_successful:
        raise Exception("Good luck next time")

    page.click("#order-another")
    return order_number

def store_receipt_as_pdf(order_number):
    page = browser.page()  
    receipt = page.locator("#order-completion").inner_html()

    pdf = PDF()
    pdf_file = f"output/receipts/receipt_for_order_{order_number}.pdf"
    
    pdf.html_to_pdf(receipt, pdf_file)
    return pdf_file

def screenshot_robot(order_number):
    page = browser.page()
    robot = page.locator("#robot-preview-image")
    screenshot_path = f"output/robots/robot_from_{order_number}.png"
    robot.screenshot(path=screenshot_path) 
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_file):
    pdf = PDF()

    pdf.add_files_to_pdf(
        files=[pdf_file, screenshot_path],
        target_document=pdf_file
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/receipts", "receipts.zip")






    




