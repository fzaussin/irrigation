# adjust x ticks for barplot so that only every Nth tick is shown
N_x = 30
ticks = ax2.xaxis.get_ticklocs()
ticklabels = [l.get_text() for l in ax2.xaxis.get_ticklabels()]
ax2.xaxis.set_ticks(ticks[::N_x])
ax2.xaxis.set_ticklabels(ticklabels[::N_x])