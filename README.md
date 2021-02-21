# greencandles


***WARNING THIS IS GUARANTEED TO HAVE BUGS.
The use of this should be for educational purposes and you are assuming your own risk. I am in no way a financial advisor, so any of the following contents or comments is ABSOLUTELY, POSITIVELY not financial advice. IF YOU USE THIS BOT AND GIVE IT MONEY TO MANAGE YOU COULD GO BROKE!!!!!***

## Setup

In order to use this bot you will need 3 things: 1. A strategy generator, 2. A highly reliable resource to run the code with a static IP, 3. An exchange account though Binance.

1. The Strategy.
	The strategy can be something of your own creation running along side the code here, or with a number of online resources. I use https://www.tradingview.com/gopro/?share_your_love=thejamestate to create a strategy and send alerts in JSON format ```{"symbol": "BSVUSD", "action": "sell"}``` based on that strategy to the interface via a webhook https://www.tradingview.com/support/solutions/43000529348-about-webhooks/. You will likely want to setup the interface to only accept messages from the IP addresses listed in the about webhooks link.
2. Web server.
	If using tradingview, you will need a server with a static IP address for the webhooks to land. There are many cloud services that you can use for this. I prefer AWS EC2. Follow these instructions.
	https://docs.aws.amazon.com/quickstarts/latest/vmlaunch/step-1-launch-instance.html
	https://aws.amazon.com/premiumsupport/knowledge-center/ec2-associate-static-public-ip/
	Allow access only from Tradingview IP addresses
	https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html
3. A Binance Account.
	Signup for a Binace account https://accounts.binance.us/en/register?ref=53413312. 
	After you create an API signup for an API key https://www.binance.com/en/support/faq/360002502072-How-to-create-API. The API key can be hard coded into the greenCandles.py library 
	```self.client = Client(clientConfig.api_key, clientConfig.api_secret, tld='us')``` as a string.

## File Descriptions

greenCandles.py creates a connection to the Binance Exchange and contains helpful functionality for RX/TX of data.

config.csv is the configuration data for the coins you would like to autopurchase. It allows for setting permissions of initial capital of a coin and stores monitoring information once the coin is purchased.

webhookInterface.py is the endpoint to TradingView webhooks. 

monitor.py monitors purchases made and added to config.csv. If the price increases it will increase a limit sell value that will allow for attempting to lock in profits as the price increases. 

dayTrader.py allows for quick purchasing and selling of a coin.

TODO: userinterface.py This will be a parser of the config.csv file and view stats in real time from a webinterface.

## Theory

The base strategy from tradingview should identify an acceptable entry point for a trade. A buy message alert is sent to the webserver and webhookInterface.py will execute a market buy of the coin. Then two selling instances can happen. If the price does not reach a certain percentage, the base strategy from tradingview sends a sell alert message and webhookInterface will sell the coin at current market value. The second instance would be if the price goes above a certain profit point and falls back down to the limit identified by monitor.py. In this case, the sell alert message from the base strategy will ignored when it arrives. Obviously, if the price falls below the limit set by the monitor program temporarily, and the price rises before the base strategy sends another buy order, you will miss out on some profits. The solution to this might be creating multiple base strategys and have one instance be a trigger for the others. The testData folder contains a visual example of a basic EMA base strategy and the take profit model. 