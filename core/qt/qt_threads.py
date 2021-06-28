from PyQt5.QtCore import Qt, QRunnable, QThread
from PyQt5.QtWidgets import *

from core.gl.gl_elements import GlModel, GlImage, GlVoxel
from core.model_processor import convert_voxels, texture_voxels, assign_blocks
from core.qt.qt_dialog import AssignBlocksDialog
from core.mc.palette_list import palette_list


class Runnable(QRunnable):
    def __init__(self, thread, thread_args, progress_dialog_label, progress_dialog_max):
        super().__init__()

        self.thread = thread(*thread_args)

        self.progress_dialog = QProgressDialog(progress_dialog_label, "Cancel", 0, progress_dialog_max)
        self.progress_dialog.setValue(0)

        # noinspection PyTypeChecker
        self.progress_dialog.setWindowFlags(
            self.progress_dialog.windowFlags() &
            Qt.CustomizeWindowHint | Qt.WindowTitleHint)

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


class ImportRunnable(Runnable):
    def __init__(self, gl_widget, files):
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

        super(ImportRunnable, self).__init__(Thread, [gl_widget, files],
                                             "".join("{0}\n".format(file) for file in files), 0)


class ConvertVoxelsRunnable(Runnable):
    def __init__(self, gl_widget):
        class Thread(QThread):
            def __init__(self, gl_widget_):
                super(Thread, self).__init__()

                self.gl_widget = gl_widget_

            def run(self):
                voxel = convert_voxels(self.gl_widget.models, self.gl_widget.grid)

                self.gl_widget.buffer_mutex.lock()
                self.gl_widget.voxels = []
                self.gl_widget.voxel_buffer.append(GlVoxel(voxel, self.gl_widget))
                self.gl_widget.buffer_mutex.unlock()

        super(ConvertVoxelsRunnable, self).__init__(Thread, [gl_widget], "Converting voxels", 0)


class TextureVoxelsRunnable(Runnable):
    def __init__(self, gl_widget):
        class Thread(QThread):
            def __init__(self, gl_widget_):
                super(Thread, self).__init__()

                self.gl_widget = gl_widget_

            def run(self):
                if not self.gl_widget.voxels:
                    return

                # from timeit import Timer
                # t = Timer(lambda: texture_voxels(self.gl_widget.voxels, self.gl_widget.images))
                # print(t.timeit(number=1))
                texture_voxels(self.gl_widget.voxels, self.gl_widget.images)

        super(TextureVoxelsRunnable, self).__init__(Thread, [gl_widget], "Texturing voxels", 0)


class AssignBlocks:
    def __init__(self, gl_widget):
        dialog = AssignBlocksDialog()
        ret = dialog.exec_()

        if ret == QMessageBox.Cancel or ret == QMessageBox.Close:
            return

        palette = palette_list[dialog.version_list.currentText()]
        if not palette:
            return

        AssignBlocksRunnable(gl_widget, palette)


class AssignBlocksRunnable(Runnable):
    def __init__(self, gl_widget, palette):
        class Thread(QThread):
            def __init__(self, gl_widget_: gl_widget, palette_):
                super(Thread, self).__init__()

                self.gl_widget = gl_widget_
                self.palette = palette_

            def run(self):
                if not self.gl_widget.voxels:
                    return

                assign_blocks(self.gl_widget.voxels[0].voxel_color,
                              self.gl_widget.voxels[0].voxels,
                              palette)
                # texture_voxels(self.gl_widget.voxels, self.gl_widget.images)

        super(AssignBlocksRunnable, self).__init__(Thread, [gl_widget, palette], "Assigning Blocks", 0)


class DeployRunnable(Runnable):
    def __init__(self, gl_widget):
        class Thread(QThread):
            def __init__(self, gl_widget_):
                super(Thread, self).__init__()

                self.gl_widget = gl_widget_

            def run(self):
                if not self.gl_widget.voxels:
                    return

                from timeit import Timer
                t = Timer(lambda: texture_voxels(self.gl_widget.voxels, self.gl_widget.images))
                print(t.timeit(number=1))
                # texture_voxels(self.gl_widget.voxels, self.gl_widget.images)

        super(DeployRunnable, self).__init__(Thread, [gl_widget], "Deploying", 0)