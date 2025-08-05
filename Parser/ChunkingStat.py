from Parser.TextBook_LumberChunker import df
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt

class Statistics:
    def __init__(self, df):
        self.plot_path = './Chunked_book_statistics.png'
        self.df = df

    def stat(self):
        self.df['content_length'] = self.df['content'].apply(len)
        variance = df['content_length'].var()
        mean = self.df['content_length'].mean()

        print(f'Mean: {mean}')
        print(f'Variance: {variance}')

    def plot_stat(self):
        sns.set_style("whitegrid")
        plt.figure(figsize=(12, 6))

        ax1 = plt.subplot(121)
        sns.histplot(data=self.df, x='content_length', bins=20, 
                    color='skyblue', edgecolor='black', alpha=0.7, kde=True)
        ax1.set_title('Length plot')
        ax1.set_xlabel('length')
        ax1.set_ylabel('frequency')

        mean_len = self.df['content_length'].mean()
        ax1.axvline(mean_len, color='red', linestyle='dashed', linewidth=1)
        ax1.text(mean_len*1.05, ax1.get_ylim()[1]*0.9, f'Mean: {mean_len:.1f}', color='red')

        ax2 = plt.subplot(122)
        sns.boxplot(data=self.df, y='content_length', color='lightgreen')
        ax2.set_title('Length box plot')
        ax2.set_ylabel('Char num')

        plt.tight_layout()
        plt.savefig('./output.png')
        plt.show()

Stat = Statistics(df)
