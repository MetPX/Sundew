#!/bin/ksh

#
# this script is a post-install used at CMC
#

# default installation ?

if [[ ! -L /var/log/px          ]]; then  rm -rf /var/log/px;            fi
if [[ ! -L /var/spool/px        ]]; then  rm -rf /var/spool/px;          fi
if [[ ! -L /etc/px              ]]; then  rm -rf /etc/px;                fi

# cmc default setup

if [[ ! -d /apps/px             ]]; then  mkdir -p /apps/px;             fi
if [[ ! -d /apps/px/db          ]]; then  mkdir -p /apps/px/db;          fi
if [[ ! -d /apps/px/etc         ]]; then  mkdir -p /apps/px/etc;         fi
if [[ ! -d /apps/px/log         ]]; then  mkdir -p /apps/px/log;         fi
if [[ ! -d /apps/px/fxq         ]]; then  mkdir -p /apps/px/fxq;         fi
if [[ ! -d /apps/px/rxq         ]]; then  mkdir -p /apps/px/rxq;         fi
if [[ ! -d /apps/px/txq         ]]; then  mkdir -p /apps/px/txq;         fi

if [[ ! -d /apps/px/etc/fx      ]]; then  mkdir -p /apps/px/etc/fx;      fi
if [[ ! -d /apps/px/etc/rx      ]]; then  mkdir -p /apps/px/etc/rx;      fi
if [[ ! -d /apps/px/etc/tx      ]]; then  mkdir -p /apps/px/etc/tx;      fi
if [[ ! -d /apps/px/etc/trx     ]]; then  mkdir -p /apps/px/etc/trx;     fi

if [[ ! -d /apps/px/etc/scripts ]]; then  mkdir -p /apps/px/etc/scripts; fi

chown -R px.px /apps/px

if [[ ! -L /var/log/px          ]]; then  ln -s /apps/px/log /var/log/px; fi
if [[ ! -L /var/spool/px        ]]; then  ln -s /apps/px   /var/spool/px; fi
if [[ ! -L /etc/px              ]]; then  ln -s /apps/px/etc     /etc/px; fi

chown px.px /var/log/px
chown px.px /var/spool/px
chown px.px /etc/px
