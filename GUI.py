#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import wx.adv
import Tkinter, tkMessageBox
from PageOne import *
from PageTwo import *
from PageThree import *


# Define the tab content as classes:

class TabOne(wx.Panel):
    def __init__(self, parent, pageOne):
        wx.Panel.__init__(self, parent)
        self.__pageOne = pageOne
        wx.StaticText(self, label='Chain 1', pos=(15, 30))
        self.__chain1 = wx.ComboBox(self, choices=self.__pageOne.getAllChains(), pos=(65, 30)) #show all the chains
        self.__chain1.Bind(wx.EVT_COMBOBOX, self.getBranches_1)
        wx.StaticText(self, label='Brunch 1', pos=(230, 30))
        self.__branch1 = wx.ComboBox(self, choices=[], pos=(285, 30), size=(170, -1))
        wx.StaticText(self, label='Chain 2', pos=(15, 85))
        self.__chain2 = wx.ComboBox(self, choices=self.__pageOne.getAllChains(), pos=(65, 85)) #show all the chains
        self.__chain2.Bind(wx.EVT_COMBOBOX, self.getBranches_2)
        wx.StaticText(self, label='Brunch 2', pos=(230, 85))
        self.__branch2 = wx.ComboBox(self, choices=[], pos=(285, 85), size=(170, -1))
        wx.StaticText(self, label='Start date', pos=(15, 135))
        self.__startDate = wx.adv.DatePickerCtrl(self, pos=(75, 135))
        wx.StaticText(self, label='End date', pos=(175, 135))
        self.__endDate = wx.adv.DatePickerCtrl(self, pos=(230, 135))
        btn = wx.Button(self, label='Find Price Coordinate!', pos=(170, 200))
        btn.Bind(wx.EVT_BUTTON, self.OnClick)

    def getBranches_1(self, event):
        self.__branch1.Set(self.__pageOne.getAllBrunchNamesInchain(self.__chain1.GetValue()))

    def getBranches_2(self, event):
        self.__branch2.Set(self.__pageOne.getAllBrunchNamesInchain(self.__chain2.GetValue()))

    def OnClick(self, event):
        if (self.__chain1.GetValue() == self.__chain2.GetValue()):
            tkMessageBox.showinfo("Error", "Please insert different Chains!")
        elif not(self.__pageOne.chainExist(self.__chain1.GetValue()) and self.__pageOne.chainExist(self.__chain2.GetValue())):
            tkMessageBox.showinfo("Error", "chain not exist!")
        elif not (self.__pageOne.branchExist(self.__chain1.GetValue(), self.__branch1.GetValue()) and (self.__pageOne.branchExist(self.__chain2.GetValue(), self.__branch2.GetValue()))):
                tkMessageBox.showinfo("Error", "branch not exist!")
        elif (self.__startDate.GetValue() > self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "please insert start date early then end date!")
        elif (self.__startDate.GetValue() == self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "can't calculate price coordinate when start data equal end date (need at least 2 days)!")
        else:
            self.__pageOne.findPriceCoordinate(self.__chain1.GetValue(), self.__branch1.GetValue(), self.__chain2.GetValue(), self.__branch2.GetValue(), self.__startDate.GetValue(), self.__endDate.GetValue())

class TabTwo(wx.Panel):
    def __init__(self, parent, pageTwo):
        wx.Panel.__init__(self, parent)
        self.__pageTwo = pageTwo
        wx.StaticText(self, label='Product', pos=(15, 30))
        self.__product = wx.ComboBox(self, choices=self.__pageTwo.getAllProducts(), pos=(65, 30))
        wx.StaticText(self, label='Chain', pos=(15, 85))
        self.__chain = wx.ComboBox(self, choices=self.__pageTwo.getAllChains(), pos=(65, 85)) #show all the chains
        self.__chain.Bind(wx.EVT_COMBOBOX, self.getBranches)
        wx.StaticText(self, label='Brunch', pos=(230, 85))
        self.__branch = wx.ComboBox(self, choices=[], pos=(275, 85), size=(170, -1))
        wx.StaticText(self, label='Start date', pos=(15, 135))
        self.__startDate = wx.adv.DatePickerCtrl(self, pos=(75, 135))
        wx.StaticText(self, label='End date', pos=(175, 135))
        self.__endDate = wx.adv.DatePickerCtrl(self, pos=(230, 135))
        btn = wx.Button(self, label='Ok', pos=(200, 200), size=(60, -1))
        btn.Bind(wx.EVT_BUTTON, self.OnClick)

    def OnClick (self, event):
        if (self.__startDate.GetValue() > self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "please insert start date early then end date!")
        else:
            plt = self.__pageTwo.getPriceForProduct(self.__product.GetValue(), self.__chain.GetValue(), self.__branch.GetValue(), self.__startDate.GetValue(), self.__endDate.GetValue())
            plt.show()


    def getBranches(self, event):
        self.__branch.Set(self.__pageTwo.getAllBrunchNamesInchain(self.__chain.GetValue()))

class TabThree(wx.Panel):
    def __init__(self, parent, pageThree):
        wx.Panel.__init__(self, parent)
        self.__pageTwo = pageThree

class MainFrame(wx.Frame):
    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        wx.Frame.__init__(self, None, title='Locating and Alerting Prices Coordinate', size=(480, 300), style=style)
        pageOne = buildPageOne()
        pageTwo = buildPageTwo()
        pageThree = buildPageThree()

        # Create a panel and notebook (tabs holder)
        panel = wx.Panel(self)
        nb = wx.Notebook(panel)

        # Create the tab windows
        tab1 = TabOne(nb, pageOne)
        tab2 = TabTwo(nb,pageTwo)
        tab3 = TabThree(nb, pageThree)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1,"Locating Prices Coordinate")
        nb.AddPage(tab2,"Prices for Product")
        nb.AddPage(tab3, "Cheapest Shopping Basket")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        sizer.Layout()

        root = Tkinter.Tk()
        root.withdraw()

if __name__ == '__main__':
    #create an application object
    app = wx.App()
    MainFrame().Show()
    #start the event loop
    app.MainLoop()

