# BritishGas MyEnergy Exporter

## Background

After having a smart meter for over 2 years, British Gas told me they had no way of giving me my data when I decided to swtich.

I started to check on Github if other have taken a stab at this problem.
I found a couple of projects that are not being maintained:
- https://github.com/ncouro/britishgas_myenergy
- https://github.com/andrew-blake/britishgas_myenergy_client

I think the login pages have changed over time and they didn't work for me.

I took the code from [ncouro](https://github.com/ncouro/britishgas_myenergy) and added updated the login function to work via selenium.

## Getting Started (on MacOS)

- Clone the repo
- `brew install geckodriver`
- `poetry install`
- `poetry run download_myenergy -u EMAIL -p PASSWORD`

Data is downloaded from `2021` onwards.
