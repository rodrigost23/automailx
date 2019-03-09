import sensors


def main():
    s = sensors.Sensors()
    print("Press Ctrl+C to terminate.\n")
    while True:
        try:
            data = s.read()
            if data is None:
                continue
            print(str(data) + "     ", end='\r')
        except KeyboardInterrupt:
            print("Interrupted." + " " * 12)
            break


if __name__ == "__main__":
    main()
