To start off, clone this branch of the repo into your local:

```bash
git clone -b main --single-branch https://github.com/aL0NEW0LF/data-playground-desktop
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
> - [x] Variance threshold feature selection
> - [x] More data processing
> - [x] More plots if possible
> - [x] Better error handling & conditions handling
> - [x] Add training & testing the model without spliting the data
> - [x] Model configuration
> - [x] Model, metrics & data visualization after training
> - [x] Better UI
> - [x] Import ML model to use
> - [ ] Add log file to record every step of the process and be able to return
> - [x] Fix the 'K-means' workflow, with more visualization of the results
> - [x] Add 3d and violent visualization
> - [x] Choose what form you want to save your file
> - [x] Add more regression models
> - [x] Add regression metrics plots
> - [ ] Add a button to show the dataset info and description on click
