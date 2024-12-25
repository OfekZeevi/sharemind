import click

from .sharemind import SharemindSecret


@click.group()
def main():
    pass


@main.command(help='Splits the given number into shares.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.argument('number', type=int)
def share(size, number):
    s = SharemindSecret(value=number, size=size)
    click.echo(f'The number {number} can be expressed with the shares {s.shares}')


@main.command(help='Reconstructs a number from a list of shares.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.argument('share_1', type=int)
@click.argument('share_2', type=int)
@click.argument('share_3', type=int)
def reconstruct(size, share_1, share_2, share_3):
    shares = (share_1, share_2, share_3)
    s = SharemindSecret(shares=shares, size=size)
    click.echo(f'The shares {shares} reconstruct to give the number {s.numeric_value}')


@main.command(help='Demo to the Sharemind multiplication and greater-than-equals.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.argument('number_1', type=int)
@click.argument('number_2', type=int)
def demo(size, number_1, number_2):
    u = SharemindSecret(value=number_1, size=size)
    v = SharemindSecret(value=number_2, size=size)
    for x in (u, v):
        click.echo(f'The number {x.numeric_value} got the shares {x.shares}')
    click.echo()

    multiplication = u * v
    click.echo(f'The multiplication of {u.numeric_value} * {v.numeric_value} gave the shares {multiplication.shares}')

    gte_result = u >= v
    click.echo(f'The GTE result of {u.numeric_value} >= {v.numeric_value} gave the shares {gte_result.shares}')


if __name__ == '__main__':
    main()
