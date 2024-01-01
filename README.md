To start off, close this cranch of the repo into your local:

```bash
git clone -b alpha/main --single-branch https://github.com/aL0NEW0LF/data-playground-desktop
```

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
> For this version, you will need to split the data into training and testing data.

> [!IMPORTANT]
> The work flow will be as follows:
>
> After starting the app:
>
> 1. Choose your wanted ML algorithm
> 2. Upload data
> 3. Choose your target column
> 4. Proccess & visualize your data
> 5. Split your dataset into training & testing data
> 6. Train & test your model, then see results

> [!NOTE]
>
> # TODO
>
> - [x] Choose target column right after uploading data
> - [ ] Variance threshold feature selection
> - [ ] More data processing
> - [ ] More plots if possible
> - [ ] Better error handling & conditions handling
> - [ ] Add training & testing the model without spliting the data
> - [ ] Model configuration
> - [ ] Model, metrics & data visualization after training
> - [ ] Better UI
