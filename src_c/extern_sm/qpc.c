/* 20/08/2016 "Light" framework version. Works only for one parent and no complex transitions */

#include "qpc.h"

#define DEBUGn                             /* n - neutralise, omit to enable */
/* \brief QEP_reservedEvt_ definition.
*/
QEvt const QEP_reservedEvt_[] = {
   { (QSignal)QEP_EMPTY_SIG_  },
   { (QSignal)Q_ENTRY_SIG     },
   { (QSignal)Q_EXIT_SIG      },
   { (QSignal)Q_INIT_SIG      }
};


QState QHsm_top(void const * const me, QEvt const * const e) {
     (void)me; /* suppress the "unused parameter" compiler warning */
     (void)e;  /* suppress the "unused parameter" compiler warning */
     return (QState)Q_RET_IGNORED; /* the top state ignores all events */
}


void QHsm_ctor (QHsm * const me, QStateHandler initial) {
  me->state.fun = Q_STATE_CAST(&QHsm_top);
  me->temp.fun  = initial;
}

void QMSM_INIT(QHsm *me, QEvt const * const e){
   (*me->temp.fun)(me, e);        /* execute the top-most initial transition */
                                                         /* enter the target */
   (void)(*me->temp.fun)(me , &QEP_reservedEvt_[Q_ENTRY_SIG]);
   
   me->state.fun = me->temp.fun; /* mark configuration as stable - MSM stuff */
}

void QMSM_DISPATCH(QHsm *me, QEvt const * const e) {
   QStateHandler s = me->state.fun;                /* save the current state */
   QStateHandler t;                             /* save state in transitions */
   QState r = (*s)(me, e);                         /* call the event handler */
   #ifdef DEBUG
      printf("dispatch: %u\n\r", r);
   #endif
   if (r == Q_RET_SUPER) {                           /* ask parent to handle */
      r = (*me->temp.fun)(me, e);                              /*pass event  */
      #ifdef DEBUG
         printf("return: %u\n\r", r);
      #endif   
   }

   if (r == Q_RET_TRAN) {                               /* transition taken? */
      t = me->temp.fun;                                       /* save target */
      (void)(*s)(me, &QEP_reservedEvt_[Q_EXIT_SIG]);      /* exit the source */
      (void)(*t)(me,&QEP_reservedEvt_[Q_ENTRY_SIG]);/*enter target*/
      me->state.fun = t;                              /* finalize transition */
   }
   if (r == Q_RET_HANDLED) {
      me->temp.fun = me->state.fun;      /* in case it was handled by parent */
   }
   
}

