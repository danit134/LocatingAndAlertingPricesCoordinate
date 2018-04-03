#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter
import os
import tkMessageBox

import wx
import wx.adv
from AppPages.PageOne import *
from AppPages.PageTwo import *
from AppPages.PageThree import *
from AppPages.mutualMethods import *
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

# Define the tab content as classes:
class TabOne(wx.Panel):
    def __init__(self, parent, pageOne, mutualMet):
        wx.Panel.__init__(self, parent)
        self.__pageOne = pageOne
        self.__mutualMet = mutualMet
        self.correlateBetweenTwoBranches = wx.CheckBox(self, id=wx.ID_ANY, label='Find correlate between two branches', pos=(5, 5))
        self.correlateInCity = wx.CheckBox(self, id=wx.ID_ANY, label='Find correlate in specific city', pos=(230, 5))
        self.correlateBetweenTwoBranches.SetValue(True)
        self.correlateInCity.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX, self.onChecked)
        self.drawCorrelateBetweenTwoBranches()

    def drawCorrelateBetweenTwoBranches(self):
        wx.StaticText(self, label='City', pos=(15, 40))
        self.__city = wx.ComboBox(self, choices=self.__mutualMet.getAllCities(), pos=(65, 40))  # show all the chains
        self.__city.Bind(wx.EVT_COMBOBOX, self.getchainsInCity)
        wx.StaticText(self, label='Chain 1', pos=(15, 80))
        self.__chain1 = wx.ComboBox(self, choices=[], pos=(65, 80), size=(150, -1))  # show all the chains
        self.__chain1.Bind(wx.EVT_COMBOBOX, self.getBranches_1)
        # self.__chain1.Bind(wx.EVT_TEXT, self.ComboChange)
        wx.StaticText(self, label='Brunch 1', pos=(230, 80))
        self.__branch1 = wx.ComboBox(self, choices=[], pos=(285, 80), size=(150, -1))
        wx.StaticText(self, label='Chain 2', pos=(15, 110))
        self.__chain2 = wx.ComboBox(self, choices=[], pos=(65, 110), size=(150, -1))  # show all the chains
        self.__chain2.Bind(wx.EVT_COMBOBOX, self.getBranches_2)
        wx.StaticText(self, label='Brunch 2', pos=(230, 110))
        self.__branch2 = wx.ComboBox(self, choices=[], pos=(285, 110), size=(150, -1))
        wx.StaticText(self, label='Start date', pos=(15, 160))
        self.__startDate = wx.adv.DatePickerCtrl(self, pos=(75, 160))
        wx.StaticText(self, label='End date', pos=(175, 160))
        self.__endDate = wx.adv.DatePickerCtrl(self, pos=(230, 160))
        wx.StaticText(self, label='Results File Path', pos=(55, 215))
        self.__dirPicker = wx.DirPickerCtrl(parent=self, id=wx.ID_ANY, message="write here", pos=(150, 210), size=(270, -1), style=wx.DIRP_DIR_MUST_EXIST | wx.DIRP_USE_TEXTCTRL | wx.DIRP_SMALL)
        # self.__dirPicker = wx.DirPickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition,wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        btn = wx.Button(self, label='Find Price Coordinate!', pos=(200, 255))
        btn.Bind(wx.EVT_BUTTON, self.OnClick_CorrelateBetweenTwoBranches)

    def getchainsInCity(self, event):
        self.__chain1.Set(self.__mutualMet.getAllChainsInCity(self.__city.GetValue()))
        self.__chain2.Set(self.__mutualMet.getAllChainsInCity(self.__city.GetValue()))
        self.__branch1.Set([])
        self.__branch2.Set([])

    def getBranches_1(self, event):
        self.__branch1.Set(self.__mutualMet.getAllBrunchNamesInchain(self.__city.GetValue(), self.__chain1.GetValue()))

    def getBranches_2(self, event):
        self.__branch2.Set(self.__mutualMet.getAllBrunchNamesInchain(self.__city.GetValue(), self.__chain2.GetValue()))

    def OnClick_CorrelateBetweenTwoBranches(self, event):
        if not (self.__mutualMet.cityExist(self.__city.GetValue())):
            tkMessageBox.showinfo("Error", "City not exist!")
        elif (self.__chain1.GetValue() == self.__chain2.GetValue()):
            tkMessageBox.showinfo("Error", "Please insert different Chains!")
        elif not(self.__mutualMet.chainExist(self.__city.GetValue(), self.__chain1.GetValue()) and self.__mutualMet.chainExist(self.__city.GetValue(), self.__chain2.GetValue())):
            tkMessageBox.showinfo("Error", "Chain not exist!")
        elif not (self.__mutualMet.branchExist(self.__city.GetValue(),self.__chain1.GetValue(), self.__branch1.GetValue()) and (self.__mutualMet.branchExist(self.__city.GetValue(), self.__chain2.GetValue(), self.__branch2.GetValue()))):
                tkMessageBox.showinfo("Error", "Branch not exist!")
        elif (self.__startDate.GetValue() > self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "Please insert start date early then end date!")
        elif (self.__startDate.GetValue() == self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "Can't calculate price coordinate when start data equal end date (need at least 2 days)!")
        elif not (os.path.isdir(self.__dirPicker.GetPath())):
            tkMessageBox.showinfo("Error","The path you insert is not a directory! try insert again")
        elif not (os.path.exists(self.__dirPicker.GetPath())):
            tkMessageBox.showinfo("Error", "The directory you insert is not exist! try insert again")
        else:
            priceCoordinateFound = self.__pageOne.findPriceCoordinate(self.__city.GetValue(), self.__chain1.GetValue(), self.__branch1.GetValue(), self.__chain2.GetValue(), self.__branch2.GetValue(), self.__startDate.GetValue(), self.__endDate.GetValue(), self.__dirPicker.GetPath())
            if (priceCoordinateFound):
                tkMessageBox.showinfo("Info", "The Coordinate Algorithm finish! Price coordinate found, check the result file")
            else:
                tkMessageBox.showinfo("Info", "The Coordinate Algorithm finish! No price coordinate found")

    def drawCorrelateInCity(self):
        wx.StaticText(self, label='City', pos=(15, 40))
        self.__city = wx.ComboBox(self, choices=self.__mutualMet.getAllCities(), pos=(65, 40))  # show all the chains
        self.__city.Bind(wx.EVT_COMBOBOX, self.getAreasInCity)
        wx.StaticText(self, label='Area', pos=(15, 70))
        self.__areaList = wx.ListBox(self,style=wx.LB_MULTIPLE, choices=[], pos=(65, 70))
        wx.StaticText(self, label='Start date', pos=(15, 160))
        self.__startDate = wx.adv.DatePickerCtrl(self, pos=(75, 160))
        wx.StaticText(self, label='End date', pos=(175, 160))
        self.__endDate = wx.adv.DatePickerCtrl(self, pos=(230, 160))
        wx.StaticText(self, label='Results File Path', pos=(55, 215))
        self.__dirPicker = wx.DirPickerCtrl(parent=self, id=wx.ID_ANY, message="write here", pos=(150, 210),size=(270, -1), style=wx.DIRP_DIR_MUST_EXIST | wx.DIRP_USE_TEXTCTRL | wx.DIRP_SMALL)
        # self.__dirPicker = wx.DirPickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition,wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        btn = wx.Button(self, label='Find Price Coordinate!', pos=(200, 255))
        btn.Bind(wx.EVT_BUTTON, self.OnClick_CorrelateInCity)

    def getAreasInCity(self, event):
        self.__areaList.Clear()
        self.__areaList.InsertItems(self.__pageOne.getAllAreasInCity(self.__city.GetValue()),0)

    def OnClick_CorrelateInCity(self, event):
        if not (self.__mutualMet.cityExist(self.__city.GetValue())):
            tkMessageBox.showinfo("Error", "City not exist!")
        elif (self.__startDate.GetValue() > self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "Please insert start date early then end date!")
        elif (self.__startDate.GetValue() == self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "Can't calculate price coordinate when start data equal end date (need at least 2 days)!")
        elif not (os.path.isdir(self.__dirPicker.GetPath())):
            tkMessageBox.showinfo("Error","The path you insert is not a directory! try insert again")
        elif not (os.path.exists(self.__dirPicker.GetPath())):
            tkMessageBox.showinfo("Error", "The directory you insert is not exist! try insert again")
        else:
            areasNames = []
            areasIndexs = self.__area.GetSelections()
            for index in areasIndexs:
                areasNames.append(self.__area.GetString(index))
            self.__pageOne.findPriceCoordinateInCity(self.__city.GetValue(), self.__startDate.GetValue(), self.__endDate.GetValue(), self.__dirPicker.GetPath())
            tkMessageBox.showinfo("Info", "The Coordinate Algorithm finish! check the results files")

    def onChecked(self, event):
        cb = event.GetEventObject()
        if (cb.GetLabel() == 'Find correlate in specific city' and cb.GetValue() == True):
            self.DestroyChildren()
            self.drawCorrelateInCity()
            self.correlateBetweenTwoBranches = wx.CheckBox(self, id=wx.ID_ANY, label='Find correlate between two branches', pos=(5, 5))
            self.correlateInCity = wx.CheckBox(self, id=wx.ID_ANY, label='Find correlate in specific city', pos=(230, 5))
            self.correlateBetweenTwoBranches.SetValue(False)
            self.correlateInCity.SetValue(True)
            self.Bind(wx.EVT_CHECKBOX, self.onChecked)
        else:
            self.DestroyChildren()
            self.drawCorrelateBetweenTwoBranches()
            self.correlateBetweenTwoBranches = wx.CheckBox(self, id=wx.ID_ANY, label='Find correlate between two branches', pos=(5, 5))
            self.correlateInCity = wx.CheckBox(self, id=wx.ID_ANY, label='Find correlate in specific city', pos=(230, 5))
            self.correlateInCity.SetValue(False)
            self.correlateBetweenTwoBranches.SetValue(True)
            self.Bind(wx.EVT_CHECKBOX, self.onChecked)


class TabTwo(wx.Panel):
    def __init__(self, parent, pageTwo, mutualMet):
        wx.Panel.__init__(self, parent)
        self.__pageTwo = pageTwo
        self.__mutualMet = mutualMet
        wx.StaticText(self, label='Product', pos=(15, 10))
        self.__product = wx.ComboBox(self, choices=self.__mutualMet.getAllProductsNames(), pos=(65, 10))
        wx.StaticText(self, label='City', pos=(15, 40))
        self.__city = wx.ComboBox(self, choices=self.__mutualMet.getAllCities(), pos=(65, 40))  # show all the chains
        self.__city.Bind(wx.EVT_COMBOBOX, self.getchainsInCity)
        wx.StaticText(self, label='Chain 1', pos=(15, 80))
        self.__chain1 = wx.ComboBox(self, choices=[], pos=(65, 80), size=(150, -1))  # show all the chains
        self.__chain1.Bind(wx.EVT_COMBOBOX, self.getBranches_1)
        wx.StaticText(self, label='Brunch 1', pos=(230, 80))
        self.__branch1 = wx.ComboBox(self, choices=[], pos=(285, 80), size=(150, -1))
        wx.StaticText(self, label='Chain 2', pos=(15, 110))
        self.__chain2 = wx.ComboBox(self, choices=[], pos=(65, 110), size=(150, -1))  # show all the chains
        self.__chain2.Bind(wx.EVT_COMBOBOX, self.getBranches_2)
        wx.StaticText(self, label='Brunch 2', pos=(230, 110))
        self.__branch2 = wx.ComboBox(self, choices=[], pos=(285, 110), size=(150, -1))
        wx.StaticText(self, label='Start date', pos=(15, 160))
        self.__startDate = wx.adv.DatePickerCtrl(self, pos=(75, 160))
        wx.StaticText(self, label='End date', pos=(175, 160))
        self.__endDate = wx.adv.DatePickerCtrl(self, pos=(230, 160))
        btn = wx.Button(self, label='Show Prices On Graph!', pos=(200, 255))
        btn.Bind(wx.EVT_BUTTON, self.OnClick)

    def getchainsInCity(self, event):
        self.__chain1.Set(self.__mutualMet.getAllChainsInCity(self.__city.GetValue()))
        self.__chain2.Set(self.__mutualMet.getAllChainsInCity(self.__city.GetValue()))
        self.__branch1.Set([])
        self.__branch2.Set([])

    def getBranches_1(self, event):
        self.__branch1.Set(self.__mutualMet.getAllBrunchNamesInchain(self.__city.GetValue(), self.__chain1.GetValue()))

    def getBranches_2(self, event):
        self.__branch2.Set(self.__mutualMet.getAllBrunchNamesInchain(self.__city.GetValue(), self.__chain2.GetValue()))

    def OnClick (self, event):
        if not (self.__mutualMet.productExist(self.__product.GetValue())):
            tkMessageBox.showinfo("Error", "Product not exist!")
        elif not (self.__mutualMet.cityExist(self.__city.GetValue())):
            tkMessageBox.showinfo("Error", "City not exist!")
        elif (self.__chain1.GetValue() == self.__chain2.GetValue()):
            tkMessageBox.showinfo("Error", "Please insert different Chains!")
        elif not(self.__mutualMet.chainExist(self.__city.GetValue(), self.__chain1.GetValue()) and self.__mutualMet.chainExist(self.__city.GetValue(), self.__chain2.GetValue())):
            tkMessageBox.showinfo("Error", "Chain not exist!")
        elif not (self.__mutualMet.branchExist(self.__city.GetValue(),self.__chain1.GetValue(), self.__branch1.GetValue()) and (self.__mutualMet.branchExist(self.__city.GetValue(), self.__chain2.GetValue(), self.__branch2.GetValue()))):
                tkMessageBox.showinfo("Error", "Branch not exist!")
        elif (self.__startDate.GetValue() > self.__endDate.GetValue()):
            tkMessageBox.showinfo("Error", "Please insert start date early then end date!")

        else:

            self.__barcode = self.__mutualMet.getBarcode(self.__product.GetValue())
            title, text1, datekey1, cost1, text2, datekey2, cost2 = self.__pageTwo.getPricesForProduct(self.__barcode, self.__city.GetValue(), self.__chain1.GetValue(), self.__branch1.GetValue(), self.__chain2.GetValue(), self.__branch2.GetValue(), self.__startDate.GetValue(), self.__endDate.GetValue())
            # plt = self.__pageTwo.getPricesForProduct(self.__barcode, self.__city.GetValue(), self.__chain1.GetValue(), self.__branch1.GetValue(), self.__chain2.GetValue(), self.__branch2.GetValue(), self.__startDate.GetValue(), self.__endDate.GetValue())
            # plt.show()
            graphFrame = wx.Frame(None, -1, title=title, size=(650, 650))
            icon = wx.Icon()
            icon.CopyFromBitmap(wx.Bitmap("Icons\\graphIcon.png", wx.BITMAP_TYPE_ANY))
            graphFrame.SetIcon(icon)
            self.fig = Figure()
            self.axes = self.fig.add_subplot(111)
            mpl.style.use('default')
            self.axes.set_title(title.format('default'), color='C0')
            self.axes.set(xlabel='Date', ylabel='Price (in Shekels)')
            self.axes.plot(datekey1, cost1, "-o", alpha=0.7, label= text1, color='red')
            self.axes.plot(datekey2, cost2, "-o", alpha=0.4, label= text2, color='blue')
            self.fig.autofmt_xdate(rotation=40)
            self.canvas = FigureCanvas(graphFrame, -1, self.fig)
            self.axes.legend()
            graphFrame.Show()

    def getBranches(self, event):
        self.__branch.Set(self.__pageTwo.getAllBrunchNamesInchain(self.__chain.GetValue()))


class TabThree(wx.Panel):
    def __init__(self, parent, pageThree, mutualMet):
        wx.Panel.__init__(self, parent)
        self.__pageTwo = pageThree
        self.__mutualMet = mutualMet

class MainFrame(wx.Frame):
    def __init__(self):
        style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        wx.Frame.__init__(self, None, title='Locating and Alerting Prices Coordinate', size=(530, 350), style=style)
        self.CenterOnScreen()
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("Icons\\appIcon.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        mutualMet = mutualMethods()
        pageOne = pageOneLogic(mutualMet)
        pageTwo = pageTwoLogic()
        pageThree = pageThreeLogic()

        # Create a panel and notebook (tabs holder)
        panel = wx.Panel(self)
        nb = wx.Notebook(panel)

        # Create the tab windows
        tab1 = TabOne(nb, pageOne, mutualMet)
        tab2 = TabTwo(nb,pageTwo, mutualMet)
        tab3 = TabThree(nb, pageThree, mutualMet)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1,"Locating Prices Coordinate")
        nb.AddPage(tab2,"Prices for Product")
        nb.AddPage(tab3, "Cheapest Shopping Basket")

        # Set notebook in a sizer to create the layout
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