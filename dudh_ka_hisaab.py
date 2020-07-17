import pandas as pd
from tkinter import *
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

df = pd.read_csv("dudh.csv")
price = 0


def add_data(date, quantity, data_frame=df, priceperlit=48):
    global price, date_entry, quantity_entry, root

    index = len(data_frame["date"])
    price = float(quantity) * priceperlit

    date_entry.delete(0, END)
    quantity_entry.delete(0, END)

    data_frame.loc[index, :] = [date, quantity, price]

    nxt_date = datetime.datetime.strptime(str(df.loc[index, "date"]), "%Y-%m-%d") + datetime.timedelta(days=1)
    date_entry.insert(0, f"{nxt_date.date()}")

    data_frame.to_csv("dudh.csv", index=False)


def monthly_bill(year, month, date2datebill="no"):
    hisaab_khata = pd.read_csv("dudh.csv")
    year_entry.delete(0, END)
    month_entry.delete(0, END)

    hisaab_khata["date"] = pd.to_datetime(hisaab_khata["date"], format="%Y-%m-%d")
    hisaab_khata.set_index(["date"], inplace=True)

    if date2datebill == "no":
        quantity_milk = hisaab_khata[f"{year}-{month}"]["quantity"].sum()
        bill = hisaab_khata[f"{year}-{month}"]["price"].sum()
    else:
        quantity_milk = hisaab_khata[f"{year}": f"{month}"]["quantity"].sum()
        bill = hisaab_khata[f"{year}": f"{month}"]["price"].sum()

    year_entry.insert(0, f"{quantity_milk} Litres")
    month_entry.insert(0, f"{bill} Rupees")

    hisaab_khata.to_csv("dudh.csv", index=True)


if __name__ == '__main__':
    milk_price = 48
    total_entries = len(df["date"])
    years = pd.DatetimeIndex(df["date"]).year
    months = pd.DatetimeIndex(df["date"]).month

    current_year = years[total_entries - 1]
    current_month = months[total_entries - 1]

    years_in_data = years.unique()

    root = Tk()
    root.title("Dudh ka Hisaab")

    date_label = Label(root, text="Date", font=[" ", 12, "bold"])
    date_label.grid(row=0, column=0, pady=(5, 5))
    date_entry = Entry(root)
    date_entry.grid(row=0, column=1, pady=(5, 5))
    last_date = datetime.datetime.strptime(str(df.loc[total_entries - 1, "date"]), "%Y-%m-%d") + \
                datetime.timedelta(days=1)
    date_entry.insert(0, f"{last_date.date()}")

    quantity_label = Label(root, text="Quantity", font=[" ", 12, "bold"])
    quantity_label.grid(row=1, column=0, pady=(5, 5))
    quantity_entry = Entry(root)
    quantity_entry.grid(row=1, column=1, pady=(5, 5))

    submit_button = Button(root, text="Submit", command=lambda: add_data(date_entry.get(), quantity_entry.get(),
                                                                         priceperlit=milk_price))
    submit_button.grid(row=2, column=0, columnspan=2, pady=(5, 5))

    year_entry = Entry(root)
    year_entry.grid(row=3, column=0, pady=(10, 5))
    month_entry = Entry(root)
    month_entry.grid(row=3, column=1, pady=(10, 5))
    year_entry.insert(0, f"{current_year}")
    month_entry.insert(0, f"{current_month}")
    check = StringVar()
    check_button = Checkbutton(root, text="Date to date bill", variable=check, onvalue="yes", offvalue="no")
    check_button.grid(row=4, column=0, columnspan=2, pady=(5, 5))
    check_button.deselect()

    bill_button = Button(root, text="Bill", command=lambda: monthly_bill(year_entry.get(), month_entry.get(),
                                                                         date2datebill=check.get()))
    bill_button.grid(row=5, column=0, columnspan=2, pady=(5, 5))

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df.set_index(["date"], inplace=True)

    quantity_milk_by_year = {}
    for yr in years_in_data:
        starting_month = 1
        months_quantity = []
        months_bill = []
        months_num = []
        while starting_month < 13:
            try:
                month_quantity = df[f"{yr}-{starting_month}"]["quantity"].sum()
                month_bill = df[f"{yr}-{starting_month}"]["price"].sum()
                months_quantity.append(month_quantity)
                months_bill.append(month_bill)
                datetime_object = datetime.datetime.strptime(f"{starting_month}", "%m")
                month_name = datetime_object.strftime("%B")
                months_num.append(month_name)
            except Exception:
                pass
            finally:
                starting_month += 1

        quantity_milk_by_year[yr] = [months_num.copy(), months_quantity.copy(), months_bill.copy()]

    plt.style.use("Solarize_Light2")
    figure = plt.figure(figsize=(4, 4))

    bar = FigureCanvasTkAgg(figure, root)
    bar.get_tk_widget().grid(row=6, columnspan=2, padx=10, pady=10)

    plt.bar([i for i in range(1, 1 + len(quantity_milk_by_year[current_year][0]))],
            quantity_milk_by_year[current_year][2])
    plt.xticks([i for i in range(1, 1 + len(quantity_milk_by_year[current_year][0]))],
               quantity_milk_by_year[current_year][0])
    plt.yticks(quantity_milk_by_year[current_year][2], [])

    for m, q, b in zip([i for i in range(1, 1 + len(quantity_milk_by_year[current_year][0]))],
                       quantity_milk_by_year[current_year][1], quantity_milk_by_year[current_year][2]):
        plt.annotate(f"Rs. {b}\n{q} Litres\nPPL Rs.{milk_price}", (m - 0.24, float(b) - 700))

    plt.xlabel(f"{current_year}")

    root.mainloop()
