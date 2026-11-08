import pygame
import time


pygame.init()
pygame.joystick.init()


print("================================")
print(" BetterRokuOS Controller Tester")
print("================================")
print()


count = pygame.joystick.get_count()


if count == 0:

    print("No controller detected.")
    print()
    print("Connect your Xbox controller and")
    print("run this program again.")

    pygame.quit()
    raise SystemExit


print(
    f"Found {count} controller(s)."
)

print()


for i in range(count):

    controller = pygame.joystick.Joystick(i)
    controller.init()

    print(
        f"[{i}] {controller.get_name()}"
    )


controller = pygame.joystick.Joystick(0)
controller.init()


print()
print(
    "Using:",
    controller.get_name()
)

print()
print("Press buttons or move the sticks.")
print("Press Ctrl+C to quit.")
print()


try:

    while True:

        for event in pygame.event.get():

            # -------------------------
            # Buttons
            # -------------------------

            if event.type == pygame.JOYBUTTONDOWN:

                print(
                    f"BUTTON {event.button} pressed"
                )


            if event.type == pygame.JOYBUTTONUP:

                print(
                    f"BUTTON {event.button} released"
                )


            # -------------------------
            # D-pad
            # -------------------------

            if event.type == pygame.JOYHATMOTION:

                x, y = event.value

                if x == -1:

                    print("D-PAD LEFT")


                elif x == 1:

                    print("D-PAD RIGHT")


                if y == -1:

                    print("D-PAD DOWN")


                elif y == 1:

                    print("D-PAD UP")


                if x == 0 and y == 0:

                    print("D-PAD CENTER")


            # -------------------------
            # Analog sticks / triggers
            # -------------------------

            if event.type == pygame.JOYAXISMOTION:

                # Ignore tiny stick noise

                if abs(event.value) < 0.15:

                    continue


                print(
                    f"AXIS {event.axis}: "
                    f"{event.value:+.2f}"
                )


            # -------------------------
            # Controller connected
            # -------------------------

            if event.type == pygame.JOYDEVICEADDED:

                print(
                    "CONTROLLER CONNECTED"
                )


            # -------------------------
            # Controller disconnected
            # -------------------------

            if event.type == pygame.JOYDEVICEREMOVED:

                print(
                    "CONTROLLER DISCONNECTED"
                )


        time.sleep(0.01)


except KeyboardInterrupt:

    print()
    print("Controller tester stopped.")


finally:

    controller.quit()

    pygame.joystick.quit()

    pygame.quit()

