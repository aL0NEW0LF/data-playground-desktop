After cloning the project, activate the env:

```bash
.venv\Scripts\activate
```

You can run the following command to install the dependencies:

```bash
pip3 install -r requirements.txt
```

Then run the main file with:

```bash
python main.py
```

2 sets of data are included, for users to test the app, first one is the titanic dataset to test all features of the app, second one is the same dataset but cleaned so the user can test training and testing the model directly.

> [!IMPORTANT]
> This app is still an alpha, which means it got developed to make specific situations and at least a workflow work.
>
> For this version, you will need to place your target column the last column and split the data into training and testing data.

> [!NOTE]
>
> # TODO
>
> - [ ] Variance threshold feature selection
> - [ ] More plots if possible
> - [ ] Better error handling & conditions handling
> - [ ] Add training & testing the model without spliting the data
> - [ ] Model, metrics & data visualization after training
> - [ ] Better UI
