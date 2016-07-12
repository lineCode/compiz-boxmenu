#!/usr/bin/env python2
from __future__ import print_function

import gtk
import gobject
from glib import GError

import re
from sys import stderr

#http://developer.gnome.org/pygtk/2.22/class-gtkicontheme.html#method-gtkicontheme--list-contexts

class IcoBrowse(gtk.Dialog):
	def __init__(self, message="", default_text='', modal=True, defaulttheme=gtk.icon_theme_get_default()):
		gtk.Dialog.__init__(self)
		if LOADED_ICONS is False:
			icobrowse_set_up(defaulttheme=defaulttheme)
		self.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE,
		      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
		self.set_title("Icon search")
		if modal:
			self.set_modal(True)
		self.set_border_width(5)
		self.set_size_request(400, 300)
		self.combobox=gtk.combo_box_new_text()
		self.combobox.set_size_request(200, 20)
		hbox=gtk.HBox(False,2)
		
		#format: actual icon, name, context
		#self.model=gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING)
		#self.modelfilter=self.model.filter_new()
		self.modelfilter=ICON_STORE.filter_new()
		self.iconview=gtk.IconView()
		self.iconview.set_model(self.modelfilter)
		self.iconview.set_pixbuf_column(0)
		self.iconview.set_text_column(1)
		self.iconview.set_selection_mode(gtk.SELECTION_SINGLE)
		self.iconview.set_item_width(72)
		self.iconview.set_size_request(200, 220)
		self.combobox.connect('changed', self.category_changed)
		self.refine=gtk.Entry()
		self.refine.connect('changed', self.category_changed)
		self.refine.set_icon_from_stock(gtk.ENTRY_ICON_SECONDARY, gtk.STOCK_FIND)
		self.refine.set_size_request(200, 30)
		self.modelfilter.set_visible_func(self.search_icons)
		for c in defaulttheme.list_contexts():
			self.combobox.append_text(c)
		self.combobox.prepend_text("Other")
		scrolled = gtk.ScrolledWindow()
		scrolled.add(self.iconview)
		scrolled.props.hscrollbar_policy = gtk.POLICY_NEVER
		scrolled.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
		hbox.add(self.combobox)
		hbox.add(self.refine)
		self.vbox.add(hbox)
		self.vbox.add(scrolled)
		self.combobox.set_active(0)
		
		self.iconview.connect('selection-changed', self.get_icon_name)
		self.vbox.show_all()

	def set_defaults(self, icon_name):
		if icon_name in {"", None}:
			return
		cmodel = self.combobox.get_model()
		for i in xrange(len(ICON_STORE)):
			if ICON_STORE[i][1] == icon_name:
				self.refine.props.text=icon_name
				for j in xrange(len(cmodel)):
					if ICON_STORE[i][2] == cmodel[j][0]:
						print(cmodel[j])
						self.combobox.set_active(j)
						break
				break

	def get_icon_name(self, widget):
		path=self.iconview.get_selected_items()
		if len(path) > 0:
			return self.modelfilter[path[0]][1]

	def category_changed(self, widget):
		self.modelfilter.refilter()

	def search_icons(self, tree, item_iter):
		category = self.combobox.get_active_text()
		icon_substr = self.refine.props.text

		cur_category = ICON_STORE.get_value(item_iter, 2)
		cur_icon_name = ICON_STORE.get_value(item_iter, 1)

		if cur_category == category:
			return icon_substr in (None, "") or re.search(icon_substr, cur_icon_name)
		else:
			return False

# leaving this here while trying to figure out how to show this
# to the user
class ProgressDialog(gtk.Dialog):
	def __init__(self, modal=True):
		gtk.Dialog.__init__(self)
		self.set_title("Loading icons...")
		if modal:
			self.set_modal(True)
		self.set_border_width(5)
		self.progress_bar = gtk.ProgressBar(adjustment=None)
		self.vbox.pack_start(self.progress_bar)
		self.show_all()

def icobrowse_set_up(defaulttheme=gtk.icon_theme_get_default()):
	print("Preloading icons")
	catted_icons=set()
	dt_contexts = defaulttheme.list_contexts()
	# pd=ProgressDialog()
	# pd.show()
	# progress = 0.
	# max_progress = len(dt_contexts)+1.

	for c in dt_contexts:
		current=defaulttheme.list_icons(context=c)
		catted_icons=catted_icons.union(set(current))
		print("Found {} icons in {}".format(len(current),c))
		#self.combobox.append_text(c)
		for i in current:
			try:
				ICON_STORE.append([defaulttheme.load_icon(i, 32,
								  gtk.ICON_LOOKUP_USE_BUILTIN),
								  i,c])
			except GError as err: stderr.write('Error loading "%s": %s\n' % (i, err.args[0]))
		# progress+=1
		# pd.progress_bar.set_fraction(progress/max_progress)

	other=list(set(defaulttheme.list_icons())-catted_icons)
	print("Placing misc. icons in Other")
	for i in other:
		ICON_STORE.append([defaulttheme.load_icon(i, 32,
								  gtk.ICON_LOOKUP_USE_BUILTIN),
								  i,"Other"])
	# progress+=1
	# pd.progress_bar.set_fraction(progress/max_progress)
	global LOADED_ICONS
	LOADED_ICONS = True


ICON_STORE=gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING)
LOADED_ICONS = False

def main():
	def misc_callback(dialog, resp):
		if resp == gtk.RESPONSE_ACCEPT:
			text = icobrowse.get_icon_name(None)
			print(text)
		icobrowse.destroy()

	import sys
	if len(sys.argv) > 1:
		theme = gtk.IconTheme()
		theme.set_custom_theme(sys.argv[1])
		icobrowse = IcoBrowse(defaulttheme=theme)
	else:
		icobrowse = IcoBrowse()

	icobrowse.connect('response', misc_callback)
	icobrowse.run()

if __name__ == '__main__':
	main()