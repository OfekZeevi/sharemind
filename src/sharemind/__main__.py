import click

from .sharemind import SharemindSecret


def _shares_to_string(shares):
    return f"({' '.join(map(str, shares))})"


@click.group()
def main():
    pass


@main.command(help='Splits the given number into shares.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.argument('number', type=int)
def share(size, number):
    s = SharemindSecret(value=number, size=size)
    click.echo(f'The number {number} can be expressed with the shares {_shares_to_string(s.shares)}')


@main.command(help='Reconstructs a number from a list of shares.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.argument('share_1', type=int)
@click.argument('share_2', type=int)
@click.argument('share_3', type=int)
def reconstruct(size, share_1, share_2, share_3):
    shares = (share_1, share_2, share_3)
    s = SharemindSecret(shares=shares, size=size)
    click.echo(f'The shares {_shares_to_string(shares)} reconstruct to give the number {s.numeric_value}')


@main.command(help='Multiply two numbers as Sharemind secrets.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.option('--auto-reconstruct', is_flag=True, default=False, help='Automatically reconstruct the shares.')
@click.argument('number_1', type=int)
@click.argument('number_2', type=int)
def multiply(size, auto_reconstruct, number_1, number_2):
    u = SharemindSecret(value=number_1, size=size)
    v = SharemindSecret(value=number_2, size=size)
    for x in (u, v):
        click.echo(f'The number {x.numeric_value} got the shares {_shares_to_string(x.shares)}')
    click.echo()

    multiplication = u * v
    click.echo(f'The multiplication of {u.numeric_value} * {v.numeric_value} '
               f'gave the shares {_shares_to_string(multiplication.shares)}')

    if auto_reconstruct:
        click.echo(f'The result reconstructs to the value {multiplication.numeric_value}')


@main.command(help='Calculate greater-than-equals between Sharemind secrets.')
@click.option('--size', default=32, type=int, help='The number of bits to use for the shares. '
                                                   'Defaults to 32.')
@click.option('--auto-reconstruct', is_flag=True, default=False, help='Automatically reconstruct the shares.')
@click.argument('number_1', type=int)
@click.argument('number_2', type=int)
def gte(size, auto_reconstruct, number_1, number_2):
    u = SharemindSecret(value=number_1, size=size)
    v = SharemindSecret(value=number_2, size=size)
    for x in (u, v):
        click.echo(f'The number {x.numeric_value} got the shares {_shares_to_string(x.shares)}')
    click.echo()

    gte_result = u >= v
    click.echo(f'The GTE result of {u.numeric_value} >= {v.numeric_value} '
               f'gave the shares {_shares_to_string(gte_result.shares)}')

    if auto_reconstruct:
        click.echo(f'The result reconstructs to the value {gte_result.numeric_value}')


if __name__ == '__main__':
    main()
