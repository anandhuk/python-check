import argparse

from src.utils.datareader import env_data_extractor as get_env_data
from src.utils.datareader import test_data_extractor as get_test_data
from src.automation.url_checker import url_checker as check_urls



def get_env(env):
    env_data = get_env_data(env)
    return env_data

def get_split_test_data(split):
    test_data = get_test_data(split)
    return test_data

def url_status(env, split, test_data):
    check_urls(env, split, test_data)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Start watchdog that accepts parameters.")
    parser.add_argument('--env', 
        type=str, 
        help='select the correct Environment dev, stage or prod'
    )
    parser.add_argument('--split', 
        type=str, 
        help='select the correct Split blog, life, app or static'
    )

    args = parser.parse_args()

    env_data = get_env(args.env)
    test_data = get_split_test_data(args.split)
    url_status(env_data, args.split, test_data)
