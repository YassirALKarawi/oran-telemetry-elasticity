"""Proposed component evidence contract, not an OpenFlow implementation."""
from dataclasses import dataclass


@dataclass
class Component:
    amount: int
    epoch: int
    state: str = 'unknown'
    compensation: str = 'none'
    version: int = -1


class Ledger:
    def __init__(self):
        self.entries = {}
        self.events = []

    def issue(self, command, component, amount, epoch):
        key = command, component
        if key in self.entries or amount <= 0:
            raise ValueError('Duplicate command/component or invalid amount')
        self.entries[key] = Component(amount, epoch)

    def timeout(self, command, component):
        # Delivery silence has no state-transition semantics.
        self.events.append(('timeout', command, component))

    def compensate(self, command, component):
        e = self.entries[command, component]
        if e.state not in ('unknown', 'applied'):
            raise ValueError('No potentially live allocation to compensate')
        e.compensation = 'pending'

    def evidence(self, command, component, epoch, version, outcome):
        e = self.entries[command, component]
        if epoch != e.epoch or version <= e.version:
            return False
        if outcome not in ('applied', 'not_applied', 'removed', 'remove_failed'):
            raise ValueError('Unrecognized evidence')
        if outcome in ('removed', 'remove_failed') and e.compensation != 'pending':
            raise ValueError('Uncorrelated compensation result')
        e.version = version
        if outcome == 'applied':
            e.state = 'applied'
        elif outcome == 'not_applied':
            e.state = 'absent'
        elif outcome == 'removed':
            e.state, e.compensation = 'absent', 'confirmed'
        else:
            e.compensation = 'failed'
        return True

    def reserved(self, component):
        return sum(e.amount for (_, c), e in self.entries.items()
                   if c == component and e.state != 'absent')

    def configuration_complete(self, command, required=('transport', 'compute')):
        return all((command, c) in self.entries and
                   self.entries[command, c].state == 'applied' and
                   self.entries[command, c].compensation == 'none'
                   for c in required)
