import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    df = pd.read_csv('./fix_results.tsv', sep='\t')
    return (df,)


@app.cell
def _(df):
    df['data'] = df['File Name'].apply(lambda x: x.split('/')[0])
    df['prova'] = df['File Name'].apply(lambda x: '/'.join(x.split('/')[:-1])) 
    df['marked'] = False
    df.loc[df['data'].isin(['13-10','14-10','15-10','16-10',]), 'marked'] = True
    return


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    df_questions = df.groupby('Question')['marked'].sum().reset_index()
    list_questions = df_questions[df_questions['marked'] > 0]['Question'].tolist()
    df.loc[df['Question'].isin(list_questions), 'marked'] = True
    return (list_questions,)


@app.cell
def _(df):
    df[df['data'].isin(['20-10','21-10'])].groupby('prova')['marked'].sum().mean()
    return


@app.cell
def _(df, list_questions):
    total = 30
    marked = df[df['data'].isin(['20-10','21-10'])].groupby('prova')['marked'].sum().mean()
    total_marked = len(list_questions)
    print(total, marked, total_marked, total_marked*total/marked)
    return


if __name__ == "__main__":
    app.run()
