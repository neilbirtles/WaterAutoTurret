import socket
import json

DEBUG=True

def yolo_model_interface(queue, event, modelparams):
    #yolo model detection server runs on the same machine on port 4141
    yolo_server_address = ('localhost', 4141)

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the yolo model server
        if DEBUG: print ('connecting to %s port %s' % yolo_server_address)
        sock.connect(yolo_server_address)
    except:
        print("Failed to connect to Yolo Model Detection Server")
    
    #wait for and process messages from the model detection server until the thread is signaled for close
    while not event.is_set():
        try:
            #string comes from c which uses a null terminator at the end so convert to utf-8 format and strip the null
            data = sock.recv(1024).decode('utf-8', "ignore")
            received_detection = json.loads(str(data).rstrip('\x00'))
            
            #if this is the initial join message then get the detection image sizes to allow scaling for movements
            if "joinmessage" in received_detection:
                modelparams.det_img_height = int(received_detection["image_height"])
                modelparams.det_img_width = int(received_detection["image_width"])
                if DEBUG: 
                    print("Detection Image Height: " + received_detection["image_height"])
                    print("Detection Image Width: " + received_detection["image_width"])
            
            if "labelname" in received_detection:
                if "person" in received_detection["labelname"]:
                    #got a detection containing a person 
                    #{'detectid': '0', 'labelname': 'person: 55% ', 'left': '868.921387', 'right': '1588.921387', 'top': '0.000000', 'bottom': '1080.000000'}
                    detection_certainty = int(str(received_detection["labelname"]).split()[1].strip('%'))
                    if detection_certainty > modelparams.detection_threshold:
                        if DEBUG: print("Got a person over detection threshold of " + str(modelparams.detection_threshold) + "%, queuing")
                        queue.put(received_detection)

        except:
            print("Error data")
            print(repr(data))
            print("-----")
