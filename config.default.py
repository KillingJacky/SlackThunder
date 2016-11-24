#This is a config template, please rename this file into 'config.py'

thunder = {
    'username': '',
    'password': '',
    'cookie_path': './cookie.txt',
    'verification_image_path': './vcode/vcode.jpg'
}

# For security consideration, the token of slack will not be hard coded.
# Instead, you should specify a env variable named "SLACK_TOKEN"

slack_channel = 'thunder'
