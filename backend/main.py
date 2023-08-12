from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import genric_helper

app = FastAPI()


inprogress_orders={}
def track_order(parameters: dict,sessio_id:str):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The Order status for order id {order_id} is : {order_status}"
    else:
        fulfillment_text = f"No Order found with order id {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def add_to_order(parameters: dict,session_id:str):
    food_items = parameters["food-item"]
    quantities = parameters['number']
    print(session_id)
    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Can you specify the food items and quantities clearly."
    else:
        new_food_dict=dict(zip(food_items,quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            for food_item,quantity in new_food_dict.items():
                if food_item in current_food_dict:
                    current_food_dict[food_item]=current_food_dict[food_item]+quantity
                else:
                    current_food_dict[food_item] = quantity
            # current_food_dict=inprogress_orders[session_id]
            # current_food_dict.update(new_food_dict)
            # inprogress_orders[session_id]=current_food_dict


        else:
            inprogress_orders[session_id]=new_food_dict

       # print('***')
        #print(inprogress_orders[session_id])

        order_str=genric_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have {order_str}.Do you need anything else?"

    #print("Response Content:", fulfillment_text)
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



@app.post("/")
async def handle_request(request:Request):
    #Retrive the JSON data from the request
    payload=await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the webhookRequest from DialogFlow

    intent=payload['queryResult']['intent']['displayName']
    parameters=payload['queryResult']['parameters']
    output_contexts=payload['queryResult']['outputContexts']

    #print(f"Received Intent: {intent}")

    session_id=genric_helper.extract_session_id(output_contexts[0]['name'])

    return intent_handler_dict[intent](parameters,session_id)


def if_incomplete_order_del(parameters:dict,session_id:str):
    del inprogress_orders[session_id]




def complete_order(parameters:dict,session_id:str):
    if session_id not in inprogress_orders:
        fulfillment_text="I'm having a trouble finding your order.Please place your order again."
    else:
        order=inprogress_orders[session_id]
        order_id=save_to_db(order)

        if order_id == -1:
            fulfillment_text="Sorry,I could'nt place your order.Please place a new order."

        else:
            order_total=db_helper.get_total_order_price(order_id)

            fulfillment_text=f"Awesome.We have placed your oder."\
                             f"Here is your order id # {order_id}.Please pay Rs.{order_total} at the time of delivery."

        del inprogress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



def save_to_db(orders:dict):
    next_order_id=db_helper.get_next_order_id()

    for food_item,quantity in orders.items():
        rcode=db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode==-1:
            return -1

        db_helper.insert_order_tracking(next_order_id,"in progress")

        return next_order_id

def remove_from_order(parameters:dict,session_id:str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order.Can you place your order again.?"
        })

    current_order=inprogress_orders[session_id]
    food_items=parameters["food-item"]

    removed_items=[]
    no_such_items=[]

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len (removed_items)>0:
        fulfillment_text=f'Removed {",".join(removed_items)} from your order.'

    if len(no_such_items)>0:
        fulfillment_text=f'Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys())==0:
        fulfillment_text += "Your order is empty"

    else:
        order_str=genric_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f"Here, is what left left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText" :fulfillment_text
    })

intent_handler_dict = {
    'order.add-context:ongoing-order': add_to_order,
    'order.complete-context:ongoing-order': complete_order,
    'order.remove-context:ongoing-order': remove_from_order,
    'track.order-context:ongoing-tracking': track_order,
    #'order.incomplete-context:ongoing-order':incomplete_order,
    'new.order':if_incomplete_order_del,
    'Default Welcome Intent':if_incomplete_order_del
}
# def add_to_order(parameters:dict):
#     food_items =parameters["food-item"]
#     quantities =parameters['number']
#
#    if len(food_items)!=len(quantities):
#        fulfillment_text="Sorry.I didn't understand.Can you specify the food items and quantities clearly."
#    else:
#        fulfillment_text=f"Received {food_items} and {quantities} in the backend."
#
#    return JSONResponse(content={
#        "fulfillmentText" : fulfillment_text
#    })

#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
