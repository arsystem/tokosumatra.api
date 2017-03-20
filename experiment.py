from vncdotool import api
import time

def run():

    time.sleep(3)
    client = api.connect('192.168.1.10', password="08133052")
    client.keyPress('d')
    time.sleep(0.1)
    client.keyPress('i')
    time.sleep(0.1)
    client.keyPress('r')
    time.sleep(0.1)
    client.keyPress("enter")
    time.sleep(0.1)

if __name__ == "__main__":
    run()
