from PyQt5.QtCore import Qt, QRunnable, QThread
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gl_elements import GlModel, GlImage
from model_processor import convert_voxels, matplotlib_show_voxel


# noinspection PyUnresolvedReferences
class ImportRunnable(QRunnable):
    def __init__(self, gl_widget, files):
        super(ImportRunnable, self).__init__()

        files = [file.toLocalFile() for file in files if
                 file.toLocalFile().split(".")[1].upper() in ["STL", "PNG", "JPG"]]
        if not files:
            return

        class Thread(QThread):
            def __init__(self, gl_widget_, files_):
                super(Thread, self).__init__()

                self.gl_widget = gl_widget_
                self.files = files_

            def run(self):
                self.gl_widget.buffer_mutex.lock()

                for file in self.files:
                    if file.split(".")[1].upper() in ["STL"]:
                        self.gl_widget.model_buffer.append(GlModel(file, self.gl_widget))
                    elif file.split(".")[1].upper() in ["PNG", "JPG"]:
                        self.gl_widget.image_buffer.append(GlImage(file, self.gl_widget))

                self.gl_widget.buffer_mutex.unlock()

        self.thread = Thread(gl_widget, files)

        self.progress_dialog = QProgressDialog("".join("{0}\n".format(file) for file in files), "Cancel", 0, 0)
        self.progress_dialog.setValue(0)

        self.progress_dialog.setWindowFlags(
            self.progress_dialog.windowFlags() &
            ~Qt.WindowCloseButtonHint &
            Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.progress_dialog.canceled.connect(self.cancel)
        self.progress_dialog.show()

    def run(self):
        self.thread.start()
        self.thread.wait()

    def cancel(self):
        self.thread.terminate()
        self.thread.wait()

        self.progress_dialog.reset()
        self.progress_dialog.close()


# noinspection PyUnresolvedReferences
class ConvertVoxelsRunnable(QRunnable):
    def __init__(self, gl_widget):
        super(ConvertVoxelsRunnable, self).__init__()

        class Thread(QThread):
            def __init__(self, progress_dialog, gl_widget_):
                super(Thread, self).__init__()

                self.progress_dialog = progress_dialog
                self.gl_widget = gl_widget_

            def run(self):
                voxels = convert_voxels(self.gl_widget.models, self.gl_widget.grid)
                # matplotlib_show_voxel(voxels, self.gl_widget.grid.grid_maxes)

        self.progress_dialog = QProgressDialog("Converting voxels", "Cancel", 0, 0)
        self.progress_dialog.setValue(0)

        self.progress_dialog.setWindowFlags(
            self.progress_dialog.windowFlags() &
            ~Qt.WindowCloseButtonHint &
            Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.progress_dialog.canceled.connect(self.cancel)
        self.progress_dialog.show()

        self.thread = Thread(self.progress_dialog, gl_widget)

    def run(self):
        self.thread.start()
        self.thread.wait()

    def cancel(self):
        self.thread.terminate()
        self.thread.wait()

        self.progress_dialog.reset()
        self.progress_dialog.close()


class TextureVoxelsRunnable(QRunnable):
    def __init__(self):
        super(TextureVoxelsRunnable, self).__init__()
        pass
