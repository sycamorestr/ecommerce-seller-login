
# 广告分组下的api

from . import _coupons_core, _deal_core, _post_core


def get_coupons(web_page, site_name, has_header=False):
    handler = _coupons_core.CouponsHandler(web_page)
    return handler.run(site_name, has_header)

def get_deal(web_page, campaignStatusFilter=None, country=""):
    handler = _deal_core.DealHandler(web_page)
    return handler.run(campaignStatusFilter, country)


# def get_campaigns(web_page, site_name):
#     handler = _campaigns_core.CampaignsHandler(web_page)
#     return handler.run(site_name)


def upload_post(web_page, post_url: str, post_type, file_path: str, title: str, asin_list: list, start_time: str, end_time: str):
    handler = _post_core.PostHandler(web_page)
    return handler.run(post_url, post_type, file_path, title, asin_list, start_time, end_time)

def main(args):

    web_page = _deal_core.xbot.web.get_active(mode="superbrowser")
    

    pass
