import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot_scores(scores1, scores2):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')

    plt.plot(scores1, color='gray')
    # plt.plot(mean_scores1)
    plt.plot(scores2, color='green')
    # plt.plot(mean_scores2)

    # plt.ylim(ymin=0)

    plt.text(len(scores1)-1, scores1[-1], str(scores1[-1]))
    # plt.text(len(mean_scores1)-1, mean_scores1[-1], str(mean_scores1[-1]))
    plt.text(len(scores2)-1, scores2[-1], str(scores2[-1]))
    # plt.text(len(mean_scores2)-1, mean_scores2[-1], str(mean_scores2[-1]))

    plt.show(block=False)
    plt.pause(.1/60)
