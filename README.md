# shotChart

shotChart is a Python project for scrapping basketball-reference.com to get the field goals attempts.

## Installation

1. `git clone git@github.com:theccalderon/shotChart.git`
2. `pip install -r requirements.txt`

## Usage
`calendar.json` has the start and end dates for NBA regular season and playoffs starting in 2000. This spider is only crawling the shots for regular season as of now.

```bash
scrapy crawl basketball-reference -o ./shotChart/data/shots-2000-wip.csv -a season=2000
```

This returns all the shots for NBA season 2000-2001. Inside the `data` dir there is Jupyter notebook (`DivingIn.ipynb`) I used to do some basic feature engineering on the scrapped data.

You can also use `execute_scrapper.sh` to get all the seasons starting in 2000 to the present.

```bash
./execute_scrapper.sh
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)
