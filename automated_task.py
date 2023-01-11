import os
import requests as re
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import ssl

def fetch_articles_until_today():
    """
     This method fetches articles from the Guardian's content API about Justin Trudeau.
    :return: pd.DataFrame: A DataFrame containing the number of articles per day for the last year
    """
    api_key = 'test'    # Replace it with your API key.
    page = 1
    results = []
    more_pages = True
    endpoint_url = "https://content.guardianapis.com/search?q=Justin Trudeau"
    today_date = datetime.now().date()

    # Load the data from the CSV file and get the last updated date
    articles_df = pd.read_csv('articles.csv', parse_dates=["webPublicationDate"])
    last_updated_date = pd.to_datetime(articles_df["webPublicationDate"].max()).date()

    # Fetch new articles only if the last updated date is older than today
    next_date = last_updated_date + timedelta(days=1) if today_date > (last_updated_date + timedelta(days=1)) else today_date
    while more_pages:
        # Make a GET request to the Guardian server to retrieve data about Justin Trudeau for the specified period
        response = re.get(endpoint_url, params = { "api-key":api_key,
                "from-date": next_date,
                "to-date": today_date,
                "show-fields" : "all",
                "page":page,
                "page-size":50,
                })
        # If the request is successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Append the results to the list of all results
            results.extend(data["response"]["results"])

            # If there are more pages of results
            if data["response"]["pages"] > page:
                # Increment the page number
                page += 1
            else:
                # Set the flag to stop the loop
                more_pages = False
        else:
            # If the request is not successful, print the status code and raise an error
            print(f"Request failed with status code {response.status_code}")
            raise ValueError("Failed to retrieve results")

    new_articles = pd.DataFrame(results)  # Create a Dataframe from the new articles retrieved
    new_articles.to_csv("articles.csv", mode='a', header=False) # Save the new articles to the CSV file
    articles_data = pd.concat([articles_df, new_articles], ignore_index=True)  # Concatenate the previous articles data with the new articles
    articles_data = articles_data.set_index('webPublicationDate')  # Set the index of the dataframe as webPublicationDate
    articles_data.index = pd.to_datetime([pd.to_datetime(i).date() for i in articles_data.index])  # convert the index to date only
    articles_data.index.name = "Date"  # Change the name of index
    latest_date = articles_data.index.max()  # Get the last date in the dataframe
    data_last_year = articles_data.loc[(articles_data.index >= latest_date - timedelta(days=365))] # Get data only from last year
    article_count_day = data_last_year.id.resample("D").count() # Resample the data by counting the ids of articles per day
    return article_count_day.to_frame('No of articles')  # return the resampled data as a DataFrame with column name 'No of articles'


def visualise_data(data_df):
    """
    This function is used to visualise the data of number of articles by plotting a line graph
    with the number of articles on the y-axis and the date on the x-axis.
    The graph is titled 'Daily Number of Articles about Justin Trudeau in The Guardian since last year'.
    The x-axis is labeled as 'Timeline' and the y-axis is labeled as 'No of Articles'
    """
    fig = px.line(data_df, x=data_df.index, y=data_df['No of articles'].values, title='Daily Number of Articles about Justin Trudeau'
    'in The Guardian since last year', labels={'y':'No of articles'})
    fig.update_layout(
                    margin=dict(l=5, r=5, b=30), #set margins for graph
                    xaxis_title='Timeline',
                    yaxis_title='No of Articles',
                    xaxis=dict(showline=True,showgrid=True,linecolor='#666666',tickfont=dict(family='poppins',color='#666666')),
                    yaxis=dict(showline=True,showgrid=True,linecolor='#666666',tickfont=dict(family='poppins',color='#666666')),
                    hoverlabel=dict(bgcolor="#ffffff",font_size=12,font_color="#141414",font_family="Calibri",bordercolor="#204ab3"),
                    plot_bgcolor='white'
                    )
    return fig


def send_email(fig, recipients):
    """
    This method sends an email to the recipients with an attachment of visualisation containing daily number of articles about JUstin Trudeau
    :param fig: figure object from visualisation method
    :param recipients: list of mail recepients
    :return:
    """
    # The smtp server and port to be used to send the email
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    # Sender email and password
    sender_email = "test@gmail.com"       # Set your email address
    password = "password"                 # Set App Password from Gmail else set it as environment variable and read it.

    # List of recipient emails
    recipient_email = recipients

    # Email body in HTML format
    html_text = """
    <!DOCTYPE html>
    <html>
      <head>
        <title> Justin Trudeau </title>
      </head>
      <body>
        <h1> Justin Trudeau </h1>
        <p> Justin Trudeau is a Canadian politician who has been the Prime Minister of Canada since 2015. He is the leader of the Liberal Party of Canada, and has served as the Member of Parliament for the electoral district of Papineau since 2008. He is the second-youngest prime minister in Canadian history, and the first to be a child of a previous prime minister. </p>
        <p> Before entering politics, Trudeau was a teacher and a snowboard instructor. He was first elected as the Member of Parliament for Papineau in 2008, and was re-elected in 2011 and 2015. In 2013, he was elected as the leader of the Liberal Party, and led the party to a majority government in the 2015 federal election. </p>
        <p>As Prime Minister, Trudeau has focused on issues such as climate change, economic growth, and reconciliation with Indigenous peoples. He has also worked to improve Canada's relationship with the United States, and has been a vocal advocate for international cooperation and multilateralism.</p>
        <i> Source Credit : chatGPT </i>
        <p> P.S : Take a look at the attachment to find the evolution of number of articles in The Guardian about Justin Trudeau in the last one year </p>
      </body>
    </html>
    """

    # Create a MIME multipart message
    message = MIMEMultipart('related')

    # Attach the HTML text to the message
    message.attach(MIMEText(html_text, 'html'))
    message["Subject"] = "Articles about Justin Trudeau in The Guardian"
    message["From"] = sender_email
    message["To"] = (',').join(recipients)

    # add visualization as attachment
    img_bytes = fig.to_image(format="png", width=800, height=600)
    image = MIMEImage(img_bytes, name="daily_update.png")
    message.attach(image)

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server,port)
        # Secure the connection
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message.as_string())
    except Exception as e:
        print(e)


if __name__ == "__main__":
    data_df = fetch_articles_until_today()
    fig = visualise_data(data_df)
    recipients = ["recipient1@gmail.com", "recipient2@gmail.com"] # Replace it with actual recepients.
    send_email(fig, recipients)