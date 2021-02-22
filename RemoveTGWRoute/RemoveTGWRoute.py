import logging
import boto3
import os

client = boto3.client('ec2', region_name=os.environ.get('REGION'))
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def static_exists(route,tgw_rt_id):
    logger.info("funct:: static_exists started... ")

    #Search if the route is already the TGW route table
    route_search = client.search_transit_gateway_routes(
        TransitGatewayRouteTableId=tgw_rt_id,
        Filters=[
            {
                'Name': 'route-search.exact-match',
                'Values': [
                    route,
                ]
            },
        ],
        MaxResults=10,
        DryRun=False
    )

    # If the route exists check if it is static
    try:
        if route_search['Routes'][0]['Type']=='static':
            logger.info("funct:: static_exists: {} route {} found in TGW RT {} ".format(route_search['Routes'][0]['Type'],route, tgw_rt_id))
            return True
        else:
            logger.info("funct:: static_exists: {} route {} found in TGW RT {} of type {} ".format(route_search['Routes'][0]['Type'],route, tgw_rt_id))
            return False
    except:
        logger.info("funct:: static_exists: route {} NOT found in TGW RT {} ".format(route, tgw_rt_id))
        return False


def lambda_handler(event, context):
    logger.info("funct:: lambda_handler started... ")
    # Configuration Variables
    tgw_rt_id=os.environ.get('TGW_ROUTE_TABLE')
    route=os.environ.get('ROUTE')

    if static_exists(route, tgw_rt_id):
        try:
            delete_result = client.delete_transit_gateway_route(
                TransitGatewayRouteTableId=tgw_rt_id,
                DestinationCidrBlock=route,
                DryRun=False
            )
            logger.info("Route {} deleted from TGW RT {} ".format(route, tgw_rt_id))
        except Exception as ex:
            logger.info("exception occured while deleting a tgw route: {} ".format(ex))
            raise

    logger.info("funct:: lambda_handler completed... ")