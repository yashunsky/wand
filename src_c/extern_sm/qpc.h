#ifndef QuasiQPC_H
#define QuasiQPC_H

#include <stdint.h>

typedef uint8_t QSignal;
typedef uint16_t QState;

typedef struct {
    QSignal sig;
} QEvt;

typedef QState(* QStateHandler) (void *const me, QEvt const *const e);

union QMAttr {
    QState state;    
    QStateHandler fun;       
};

enum {
    QEP_EMPTY_SIG_ = 0,
    Q_ENTRY_SIG,  
    Q_EXIT_SIG,       
    Q_INIT_SIG,       
    Q_USER_SIG        
};

enum {
     Q_RET_SUPER,
     Q_RET_HANDLED,
     Q_RET_IGNORED, 
     Q_RET_TRAN,      
};

typedef struct {
     union QMAttr state;   
     union QMAttr temp;    
} QHsm;

//!typedef struct QHsmTag { /* Partly hierarchical State Machine */
//!   QStateHandler state; /* current active state */
//!} QHsm;

#define Q_MSM_UPCAST(ptr_) ((QHsm *)(ptr_))
#define Q_STATE_CAST(handler_) ((QStateHandler)(handler_))
#define Q_HANDLED() ((QState)Q_RET_HANDLED)
#define Q_TRAN(target_) \
      ((Q_MSM_UPCAST(me))->temp.fun = Q_STATE_CAST(target_), (QState)Q_RET_TRAN)
#define Q_SUPER(super_) \
      ((Q_MSM_UPCAST(me))->temp.fun = Q_STATE_CAST(super_), (QState)Q_RET_SUPER)

void QMSM_INIT(QHsm *me, QEvt const * const e);
void QMSM_DISPATCH(QHsm *me, QEvt const * const e);
void QHsm_ctor(QHsm * const me, QStateHandler initial);
QState QHsm_top(void const * const me, QEvt const * const e);

#endif
