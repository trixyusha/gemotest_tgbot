from math import ceil
from .database.requests import city_requests, research_requests, service_requests, action_requests, order_requests

async def researches(data, tg_id, only_dict = False):
    ids = data.split('#')
    research_category_id = int(ids[0])
    research_subcategory_id = int(ids[1])
    city_id = await city_requests.get_city_id(tg_id)
    print(f'[RESEARCH] CITY ID {city_id}')
    research_subcategory_name = await research_requests.get_research_subcategory_name(research_subcategory_id)
    researches = await research_requests.get_researches(research_category_id, research_subcategory_id, city_id)
    res_dict = {}
    rlist = [[i.ID, i.Name, i.ResearchCategoryID, i.ResearchSubcategoryID] for i in researches]
    # print(f'\n\nRESEARCHES\n{rlist}\n\n')
    count = len(rlist)
    pages_count = ceil(count/10)
    split = lambda lst, n: [lst[i::n] for i in range(n)]
    for i, item in enumerate(split(rlist, pages_count), start = 1):
        res_dict[i] = item
    if only_dict:
        return res_dict
    else: return research_subcategory_name, count, res_dict

async def services(data, tg_id, only_dict = False):
    city_id = await city_requests.get_city_id(tg_id)
    ids = data.split('#')
    service_category_id = int(ids[0])
    service_subcategory_id = int(ids[1])
    service_subcategory_name = await service_requests.get_service_subcategory_name(service_subcategory_id)
    services = await service_requests.get_services(service_category_id, service_subcategory_id, city_id)
    serv_dict = {}
    slist = [[i.ID, i.Name, i.ServiceCategoryID, i.ServiceSubcategoryID] for i in services]
    count = len(slist)
    pages_count = ceil(count/10)
    split = lambda lst, n: [lst[i::n] for i in range(n)]
    for i, item in enumerate(split(slist, pages_count), start = 1):
        serv_dict[i] = item
    if only_dict:
        return serv_dict
    else: return service_subcategory_name, count, serv_dict

async def actions(data, only_dict = False):
    ids = data.split('#')
    action_category_id = int(ids[0])
    action_subcategory_id = int(ids[1])
    action_subcategory_name = await action_requests.get_action_subcategory_name(action_subcategory_id)
    actions = await action_requests.get_actions(action_category_id, action_subcategory_id)
    act_dict = {}
    alist = [[i.ID, i.Name, i.Description, i.ActionCategoryID, i.ActionSubcategoryID] for i in actions]
    # print(f'\n\nRESEARCHES\n{rlist}\n\n')
    count = len(alist)
    pages_count = ceil(count/10)
    split = lambda lst, n: [lst[i::n] for i in range(n)]
    for i, item in enumerate(split(alist, pages_count), start = 1):
        act_dict[i] = item
    if only_dict:
        return act_dict
    else: return action_subcategory_name, count, act_dict

async def orders(tg_id, only_dict = False):
    orders = await order_requests.get_orders(tg_id)
    if orders:
        orders_dict = {}
        olist = [[i.ID, i.OrderNum, i.RegistrationDate] for i in orders]
        count = len(olist)
        pages_count = ceil(count/10)
        split = lambda lst, n: [lst[i::n] for i in range(n)]
        for i, item in enumerate(split(olist, pages_count), start = 1):
            orders_dict[i] = item
        if only_dict:
            return orders_dict
        else: return count, orders_dict
    else: return None, None

async def get_cat_subcat_names(cat_id, subcat_id, what_is):
    cat_id = int(cat_id)
    subcat_id = int(subcat_id)
    if what_is  ==  'research':
        cat = await research_requests.get_research_categories(None, cat_id)
        subcat_name = await research_requests.get_research_subcategory_name(subcat_id)
        # print(f'\nGET CATEGORY AND SUBCATEGORY RESEARCH NAMES\nCATEGORY NAME {cat.Name} SUBCATEGORY NAME {subcat_name}\n')
        return cat.Name, subcat_name
    elif what_is  ==  'service':
        cat = await service_requests.get_service_categories(None, cat_id)
        subcat_name = await service_requests.get_service_subcategory_name(subcat_id)
        # print(f'\nGET CATEGORY AND SUBCATEGORY SERVICE NAMES\nCATEGORY NAME {cat.Name} SUBCATEGORY NAME {subcat_name}\n')
        return cat.Name, subcat_name
    elif what_is  ==  'action':
        cat = await action_requests.get_action_categories(cat_id)
        subcat_name = await action_requests.get_action_subcategory_name(subcat_id)
        # print(f'\nGET CATEGORY AND SUBCATEGORY RESEARCH NAMES\nCATEGORY NAME {cat.Name} SUBCATEGORY NAME {subcat_name}\n')
        return cat.Name, subcat_name
