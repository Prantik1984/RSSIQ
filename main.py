import sys
from urllib.parse import urlparse
from Operators.FeedOperator import FeedOperator
from Operators.ChromaOperator import ChromaOperator
""""
declaring variables
"""
operation_type=feed_url=user_query=None

def main():
    """"
    Main function
    """
    global operation_type, feed_url,user_query

    for arg in sys.argv:
        if arg.startswith('-o'):
            operation_type=arg[2:]

        if arg.startswith('-f'):
            feed_url=arg[2:]

        if arg.startswith('-q'):
            user_query=arg[2:]

    validate_input()
    chroma_operator = ChromaOperator()

    match(operation_type):
        case 'add':
            feed_operator=FeedOperator()
            feed_details = feed_operator.get_feed_details(feed_url)
            if len(feed_details) == 0:
                print("No feed details found")
                sys.exit(1)


            chroma_operator.save_rss_details(feed_details)
        case 'download':
            chroma_operator.complete_downloads()

        case 'query':
            chroma_operator.search_db(user_query)

        case _:
            print("Unkown operation")



def validate_input():
     """"
     validates the inputs
     """
     if not operation_type or operation_type not in ['add','download','query']:
         print("Operation type is not valid")
         sys.exit(1)

     if operation_type == 'add':
         if not feed_url:
            print("Feed url is not provided")
            sys.exit(1)

         parsed = urlparse(feed_url)
         if not all([parsed.scheme, parsed.netloc]):
             print("Feed url is not valid")
             sys.exit(1)




if __name__ == '__main__':
    main()